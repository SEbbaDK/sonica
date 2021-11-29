#!/usr/bin/env python3

import asyncio
import websockets
from typing import Dict, List
import sys
import json

from sonica_pb2_grpc import SonicaStub
from validate import validate
# from sonica_pb2 import


api_methods = {}


def api_method(name: str, scheme = None):
    def decor(method_func):
        global api_methods

        def wrapper(socket, value):
            return method_func(socket, validate(scheme, value))

        api_methods[name] = wrapper
        return wrapper
    return decor


@api_method("test", {"hej": int, "lol": [str]})
def test(socket, value):
    print("got test message", value)


async def echo(websocket, hello):
    print(hello)
    async for message in websocket:
        message = json.loads(message)
        message = validate({"method": str, "value": None}, message)
        print("hej", message, type(message))
        method = api_methods[message["method"]]
        method(websocket, message["value"])


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
