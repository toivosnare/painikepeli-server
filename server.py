#!/usr/bin/env python

import os
import asyncio
import websockets
import json

INITIAL_SCORE = 20
players = {}
counter = 0

def get_score(player):
    return {
        "action" : "updateScore",
        "score" : players[player]
    }

def reset(player):
    print(f"Reseting {player}'s score to {INITIAL_SCORE}")
    players[player] = INITIAL_SCORE
    
def join(player):
    if player not in players:
        reset(player)

def tap(player):
    global counter

    players[player] -= 1
    counter += 1
    prize = 0
    if counter % 10 == 0:
        prize = 5
    if counter % 100 == 0:
        prize = 40
    if counter % 500 == 0:
        prize = 250
    players[player] += prize
    taps_until_prize = 10 - counter % 10

    return {
        "type" : "tapResult",
        "prize" : prize,
        "newScore" : players[player],
        "tapsUntilPrize" : taps_until_prize
    }

async def respond(websocket, path):
    msg = json.loads(await websocket.recv())
    try:
        action = msg["action"]
        player = msg["player"]
    except KeyError:
        print("Invalid message: ", msg)
        return

    if action == "join":
        join(player)
        response = get_score(player)
    elif action == "tap":
        response = tap(player)
    elif action == "reset":
        reset(player)
        response = get_score(player)
    else:
        print("Invalid message: ", msg)
        return
    
    print("Sending response: ", response)
    await websocket.send(json.dumps(response))
    

port = os.environ['PORT']
host = "0.0.0.0"
print("Starting server on port", port)
start_server = websockets.serve(respond, host, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
