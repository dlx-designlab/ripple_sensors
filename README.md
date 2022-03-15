# RIPPLE SENSORS

A collection of scripts used to simulate and connect varios sensors to the "Ripple Floor" system.  

## General Important dependencies:
 - `pip3 install python-socketio`

## Multi Lidar Scanner SIO:
Used to get data from the LIDAR sensors and send it over via socketIO to the Ripple server  
### Dependencies:
- `pip3 install pyrplidar`
- `pip install numpy`

## RFID SIO:
Used to get data from an RFID card scanner, load the relevant data from the `passengers_data.json` and send it oevr to the Ripple Server.

### Dependencies:
- x11-utils: `apt-get install x11-utils` 
- wmctrl: `apt-get install wmctrl` 
- Python Dependencies: `pip3 install attrs wmctrl`

