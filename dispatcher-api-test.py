import asyncio
import websockets
import os
import json
import csv
import requests


# Get a token from https://dispatcher.jp/oapi/v1/tokens
# IMPORTANT: Set the OS variabe in advance via "export DISPATCHER_API_KEY=<the_key>"
api_key = os.environ['DISPATCHER_API_KEY']
url = "https://oapi.dev.dispatcher.jp/v1/auth/token"
header = {"Authorization": f"Bearer {{{api_key}}}"}
res = requests.get(url, headers=header).json()
token = res['token']
# print(res)
# print(token)


async def get_bus_data():        
    async with websockets.connect(f"wss://message.dev.dispatcher.jp/oapi/v1/ws/vehicle/states?access_token={token}") as websocket:
        
        f = open('bus_locations_data.csv', 'w')
        csv_writer = csv.writer(f)
        csv_writer.writerow(['lat', 'lon'])

        try:
            while True:
                # await websocket.send("Hello world!")
                message = await websocket.recv()
                data = json.loads(message)
                print(data)

                # log points of interest in csv file
                if data['speed'] > 5:   
                    pos_data = [data["lat"], data["lon"]]
                    csv_writer.writerow(pos_data)
                        
        except KeyboardInterrupt:
            f.close()
            pass



asyncio.run(get_bus_data())