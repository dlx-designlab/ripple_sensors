# Ripple Sensors 📡

A collection of scripts used to simulate and connect various sensors to the [Ripple Floor](https://github.com/dlx-designlab/ripple_js) system.  

### General Important Dependencies
 - Python 3.7 and above
 - `pip3 install python-socketio`
 - `pip3 install websockets`

## Multi Lidar Scanner SIO
Used to get data from the LIDAR sensors and send it over via socketIO to the Ripple server  

### Dependencies
- `pip3 install pyrplidar`
- `pip install numpy`
- `pip3 install python-socketio`
- on Nvidia Jetson: sudo apt-get install python3-numpy
- opencv

## RFID SIO
Used to get data from an RFID card scanner, load the relevant data from the `passengers_data.json` and send it oevr to the Ripple Server.

### Dependencies
- x11-utils: `apt-get install x11-utils` 
- wmctrl: `apt-get install wmctrl` 
- Python Dependencies: `pip3 install attrs wmctrl`

## GPS Playback
This python script can be used to playback `.gpx.` GPS recordings for user experiements and testing.
```
python gpsPlayback.py xml/kashiwa.gpx
```

### Dependencies
- `pip install -r requirements.txt`


## Boldly Dispatcher API Test
Used to test Communcation with the NAVYA Busses Server Operated by Softbank Boldly  
- You will need to get an API Key from (Production or Dev).  
- You need to set an OS variabe in advance via `export DISPATCHER_API_KEY=the_api_key`
- Python 3.7 and above is required