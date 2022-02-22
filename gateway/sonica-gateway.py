#!/usr/bin/env python3

import asyncio
import websockets
import typer
import json
import grpc
import traceback
import typer

from sonica_pb2_grpc import SonicaStub
from validate import validate, ValidationException
# from sonica_pb2 import

from methods import api_methods, api_method, ApiException

verbose_mode = False

cli = typer.Typer()

# TODO, sanitation on the stuff we return here?
def handle_message(raw_msg, sonica, websocket):
    error_resp = {"type": "Error", "value": {}, "channel": None}

    try:
        message = validate({"channel": int, "type": str, "value": dict}, raw_msg)
    except ValidationException as e:
        error_resp["channel"] = raw_msg["channel"]
        error_resp["value"]["message"] = str(e)
        return error_resp

    error_resp["channel"] = message["channel"]

    methodname = message["type"]
    if methodname not in api_methods:
        error_resp["value"]["message"] =  f"no such method '{methodname}'"
        return error_resp

    response = {"type": "", "value": {}, "channel": message["channel"]}
    try:
        type, ret = api_methods[methodname](sonica, websocket, message["value"])
        response["value"] = ret
        response["type"] = type
    except (ValidationException, ApiException) as e:
        error_resp["value"]["message"] = str(e)
        return error_resp
    except Exception as e:
        # If we throw here we stall the websocket,
        # so catch everything and print it
        print(e)
        error_resp["value"]["message"] = "general server error"
        return error_resp

    return response


async def server_start(sonica, host, port):
    print(f"Listening for websocket connections on {host}:{port}")

    async def echo(websocket, hello):
        async for message in websocket:
            if verbose_mode:
                print("\nReceived: " + message)
            try:
                message = json.loads(message)
                response = handle_message(message, sonica, websocket)
                json_response = json.dumps(response)
                if verbose_mode:
                    print("\nSent:     " + json_response[0:120])
                await websocket.send(json_response)
            except json.JSONDecodeError as e:
                response = { "channel" : 0, "type" : "Error", "value" : { "message" : "Invalid JSON" } }
                json_response = json.dumps(response)
                if verbose_mode:
                    print("\nSent:     " + json_response[0:120])
                await websocket.send(json_response)
            except Exception as e:
                response = { "channel" : 0, "type" : "Error", "value" : { "message" : "Internal server error" } }
                json_response = json.dumps(response)
                if verbose_mode:
                    print("\nSent:     " + json_response[0:120])
                await websocket.send(json_response)
                print("Encountered internal server error:")
                raise e

    async with websockets.serve(echo, host, port):
        await asyncio.Future()

@cli.command()
def cli(
        sonica_host: str = "localhost",
        sonica_port: int = 7700,
        listen_host: str = "localhost",
        listen_port: int = 7701,
        verbose : bool = False
        ):
    global verbose_mode
    verbose_mode = verbose
    address = f"{sonica_host}:{sonica_port}"
    print(f"Connecting to daemon at {address}")
    channel = grpc.insecure_channel(address)
    stub = SonicaStub(channel)

    asyncio.run(server_start(stub, listen_host, listen_port))


if __name__ == "__main__":
    typer.run(cli)
