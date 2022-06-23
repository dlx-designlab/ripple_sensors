import asyncio
import websockets
import os
import json
import csv
import requests

# IMPORTANT:    Set the OS variabe in advance via "export DISPATCHER_API_KEY=<the_key>" to the Correct API Key
#               And Adjust the variable below for the correct working environment DEV or PROD
PRODUCTION_MODE = False

if PRODUCTION_MODE:
    print("!!! PRODUCTION Mode !!!")
    #Dispatcher PRODUCTION Servers
    token_server_url = "https://oapi.dispatcher.jp/v1/auth/token"
    dispatcher_server_url = "wss://message.dispatcher.jp/oapi/v1/ws/vehicle/states"

else:
    print("@@@ DEVELOPMENT Mode @@@ ")
    #Dispatcher DEV Servers
    token_server_url = "https://oapi.dev.dispatcher.jp/v1/auth/token"
    dispatcher_server_url = "wss://message.dev.dispatcher.jp/oapi/v1/ws/vehicle/states"

# Get a token from https://oapi.dispatcher.jp/v1/auth/token
print("Requesting token from the Dispatcher Server...")
api_key = os.environ['DISPATCHER_API_KEY']
header = {"Authorization": f"Bearer {{{api_key}}}"}
res = requests.get(token_server_url, headers=header).json()
token = res['token']
print(f"got response: {res}")


print("Getting bus data...")
async def get_bus_data():        

    async with websockets.connect(f"{dispatcher_server_url}?access_token={token}") as websocket:

        f = open('bus_locations_data.csv', 'w')
        csv_writer = csv.writer(f)
        csv_writer.writerow(['lat', 'lon'])

        try:
            while True:
                
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