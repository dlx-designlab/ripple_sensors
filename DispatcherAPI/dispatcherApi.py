import asyncio
import csv
import json
import os
import requests
import socketio
import websockets


# Get a token from https://dispatcher.jp/oapi/v1/tokens
# IMPORTANT: Set the OS variabe in advance via "export DISPATCHER_API_KEY=<the_key>"
api_key = os.environ['DISPATCHER_API_KEY']

# url = "https://oapi.dev.dispatcher.jp/v1/auth/token"
url = "https://oapi.dispatcher.jp/v1/auth/token"

header = {"Authorization": f"Bearer {{{api_key}}}"}
print('Getting token.')
res = requests.get(url, headers=header).json()
token = res['token']
print('Token received.')

sio = socketio.Client()

print('Connecting to Ripple server.')
try:
  sio.connect('http://localhost:3000')
except socketio.exceptions.ConnectionError as err:
  print("Error connecting to Ripple server:\n", err)
  exit()
else:
  print('Connection to Ripple server established.')

# wss = f"wss://message.dev.dispatcher.jp/oapi/v1/ws/vehicle/states?access_token={token}"
wss = f"wss://message.dispatcher.jp/oapi/v1/ws/vehicle/states?access_token={token}"

async def get_bus_data():        
  async with websockets.connect(wss) as websocket:
    print('Connection to Dispatcher API established.')
    print('Streaming data.')

    index = 0;

    try:
      while True:
        message = await websocket.recv()
        data = json.loads(message)
        update = {'lat': data["lat"], 'lon': data["lon"]}
        sio.emit('updateGps', update)
        sio.emit('updatespeed', data["speed"])
        index += 1;
        print("%d updates forwarded." % index, end='\r')

    except KeyboardInterrupt:
      f.close()
      pass

asyncio.run(get_bus_data())
