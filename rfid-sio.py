
import socketio

import sys
print("Python version")
print (sys.version)

users = {
    "0003210808": "user_01",
    "0003225772": "user_02",
    "0003234054": "user_03"    
}

sio = socketio.Client()

if __name__ == "__main__":
    
    # setup socket io client
    sio.connect('http://localhost:3000')
    print("Connected to Ripple Server!")

    try:
        while True:
            value = input("Please swipe your card: ")
            print(f'Welcome onboard {users[value]} !!')
            sio.emit("payment",users[value])

    except KeyboardInterrupt:
        pass

    # sio.wait()
