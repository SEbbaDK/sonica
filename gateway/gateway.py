#!/usr/bin/env python3

import asyncio
import websockets
from typing import Dict, List
import sys
import json
import grpc

from sonica_pb2_grpc import SonicaStub
from validate import validate
# from sonica_pb2 import

from methods import api_methods, api_method


@api_method("test", {"hej": int, "lol": [str]})
def test(sonica, socket, value):
    print("got test message", value)


async def main(sonica):
    print("Ready")

    async def echo(websocket, hello):
        print("Got connection")
        async for message in websocket:
            message = json.loads(message)
            message = validate({"method": str, "value": None}, message)
            method = api_methods[message["method"]]
            name, resp = method(sonica, websocket, message["value"])
            await websocket.send(json.dumps({
                "type": name,
                "value": resp
            }))

    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    channel = grpc.insecure_channel("localhost:7700")

    stub = SonicaStub(channel)
    asyncio.run(main(stub))
