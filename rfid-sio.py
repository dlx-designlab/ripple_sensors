from curses import window
import json
import time
import socketio
import threading
from wmctrl import Window #requires: 'pip3 install attrs wmctrl'


import sys
print("Python version")
print (sys.version)

# Window control
# wins = Window.list()
# print(wins)
# names = [win.wm_name for win in wins]
# print(names)

# get the currenly active window data
# my_window = Window.by_name("pi@raspberrypi: ~/projects/ripple_sensors")[0]
my_window = Window.get_active()
print(my_window)

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


def keep_window_in_focus(selected_window, freq):
    while selected_window:
        selected_window.activate()
        time.sleep(freq)


if __name__ == "__main__":
    
    # setup socket io client
    sio.connect(f'http://{settings["server_ip"]}:3000')
    print("Connected to Ripple Server!")
    
    # a thread to keep the script window in focus
    keepInFocus = threading.Thread(target=keep_window_in_focus, args=(my_window, 5,))
    keepInFocus.start()

    try:
        while True:
            value = input("Please swipe your card: ")
            print(f'Welcome onboard {users[value]} !!')
            sio.emit("updatepassenger",{"id": users[value]["id"], "scanned": True, "destination": users[value]["dest_stop_id"]})
            
    except KeyboardInterrupt:
        pass

    # sio.wait()