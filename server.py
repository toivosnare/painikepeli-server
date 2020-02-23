#!/usr/bin/env python

import os
import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

port = os.environ['PORT']
host = "localhost"
print("Starting server on port", port)
start_server = websockets.serve(hello, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
