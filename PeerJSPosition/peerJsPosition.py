from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import random
import webbrowser

app = Flask(__name__)
socketio = SocketIO(app)
thread = None


def background_thread():
    while True:
        socketio.emit('updatepassenger', {
            'id': 1,
            'position': {
                'x': random.randrange(100),
                'y': random.randrange(100),
            }
        })
        time.sleep(0.1)


@socketio.on('connect')
def connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    webbrowser.open('http://0.0.0.0:8000/')
    socketio.run(app, host='0.0.0.0', port=8000)
