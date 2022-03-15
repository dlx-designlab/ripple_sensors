import asyncio
import websockets
import os
import json

# set the OS variabe in advance via "export DISPATCHER_ACCESS_TOKEN=<the_token>"
# get token from system environment variable
token = os.environ['DISPATCHER_ACCESS_TOKEN']

async def get_bus_data():        
    async with websockets.connect(f"wss://message.dev.dispatcher.jp/oapi/v1/ws/vehicle/states?access_token={token}") as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(data['speed'])
            # await websocket.send("Hello world!")


asyncio.run(get_bus_data())