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
    error_resp = {"type": "error", "value": "", "token": None}

    try:
        message = validate({"token": int, "method": str, "value": None}, raw_msg)

    except ValidationException as e:
        error_resp["value"] = str(e)
        return error_resp

    error_resp["token"] = message["token"]

    methodname = message["method"]
    if methodname not in api_methods:
        error_resp["value"] =  f"no such method '{methodname}'"
        return error_resp

    response = {"type": "return", "value": {}, "token": message["token"]}
    try:
        type, ret = api_methods[methodname](sonica, websocket, message["value"])
        response["value"] = ret
        response["value_type"] = type
    except (ValidationException, ApiException) as e:
        error_resp["value"] = str(e)
        return error_resp
    except Exception as e:
        # If we throw here we stall the websocket,
        # so catch everything and print it
        print(e)
        error_resp["value"] = "general server error"
        return error_resp

    return response


async def main(sonica):
    print("Ready")

    async def echo(websocket, hello):
        print("Got connection")
        async for message in websocket:
            message = json.loads(message)
            response = handle_message(message, sonica, websocket)
            await websocket.send(json.dumps(response))

    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    channel = grpc.insecure_channel("localhost:7700")

    stub = SonicaStub(channel)
    asyncio.run(main(stub))
