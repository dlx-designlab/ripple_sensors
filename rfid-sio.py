import json
import socketio

import sys
print("Python version")
print (sys.version)

f = open("passengers_data.json")
users = json.load(f)
f.close()

f = open("system_settings.json")
settings = json.load(f)
f.close()


sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    print('disconnected from server')

if __name__ == "__main__":
    
    # setup socket io client
    sio.connect(f'http://{settings["server_ip"]}:3000')
    print("Connected to Ripple Server!")

    try:
        while True:
            value = input("Please swipe your card: ")
            print(f'Welcome onboard {users[value]} !!')
            sio.emit("updatepassengerbalance",{"id": users[value]["id"], "balance": users[value]["balance"]})
            
    except KeyboardInterrupt:
        pass

    # sio.wait()
