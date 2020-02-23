#!/usr/bin/env python

import os
import asyncio
import websockets
import json

players = {}
counter = 0

async def response(websocket, path):
    msg = json.loads(await websocket.recv())
    name = msg["name"]
    if name not in players:
        players[name] = 20
    websocket.send(str(players[name]))
    

port = os.environ['PORT']
host = "0.0.0.0"
print("Starting server on port", port)
start_server = websockets.serve(response, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
