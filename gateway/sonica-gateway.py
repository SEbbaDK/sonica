#!/usr/bin/env python3

import asyncio
import websockets
from typing import Dict, List
import sys
import json
import grpc
import traceback

from sonica_pb2_grpc import SonicaStub
from validate import validate, ValidationException
# from sonica_pb2 import

from methods import api_methods, api_method, ApiException


@api_method("test", {"hej": int, "lol": [str]})
def test(sonica, socket, value):
    print("got test message", value)


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


async def main(sonica, host, port):
    print(f"Listening for websocket connections on {host}:{port}")

    async def echo(websocket, hello):
        print("Got connection")
        async for message in websocket:
            print("Received: " + message)
            try:
                message = json.loads(message)
                response = handle_message(message, sonica, websocket)
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError as e:
                await websocket.send(json.dumps({ "channel" : 0, "type" : "Error", "value" : { "message" : "Invalid JSON" } }))
            except Exception as e:
                await websocket.send(json.dumps({ "channel" : 0, "type" : "Error", "value" : { "message" : "Internal server error" } }))
                print("Encountered internal server error:")
                raise e

    async with websockets.serve(echo, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    address = "localhost:7700" 
    print(f"Connecting to daemon at {address}")
    channel = grpc.insecure_channel(address)
    stub = SonicaStub(channel)

    host = "localhost"
    port = 7701
    asyncio.run(main(stub, host, port))
