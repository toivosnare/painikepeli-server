#!/usr/bin/env python

# Basic server that keep track of players scores and mediates
# the information to clients via websockets. Transfered data
# is formatted in simple json format. No real user authentication
# is performed by the server for now (other than the player name
# identifier attached to all messages).

import os
import asyncio
import websockets
import json
import signal

INITIAL_SCORE = 20
players = {} # Dictionary with player names as keys and their scores as values
counter = 0

def get_score(player):
    return {
        "action" : "updateScore",
        "score" : players[player]
    }

def reset(player):
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
        "action" : "tapResult",
        "prize" : prize,
        "newScore" : players[player],
        "tapsUntilPrize" : taps_until_prize
    }

async def respond(websocket, path):
    try:
        async for message in websocket:
            message = json.loads(message) # Decode json string to a dict object
            try:
                action = message["action"]
                player = message["player"]
            except KeyError:
                print("Invalid message: ", message)
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
                print("Invalid message: ", message)
                return
            print(">", message)
            print("<", response)
            await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed: # If connection closes abruptly
        return
    
async def game_server(stop):
    host = "0.0.0.0"
    port = os.environ["PORT"] # Get the port reserved by Heroku from environment variables
    print("Starting server on port", port)
    async with websockets.serve(respond, host, port):
        await stop

loop = asyncio.get_event_loop()
stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None) # To shutdown gracefully on sigterm signal 
loop.run_until_complete(game_server(stop))
