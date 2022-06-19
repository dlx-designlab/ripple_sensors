from datetime import datetime
import socketio
import sys
import time
import xml.etree.ElementTree as ET


sio = socketio.Client()

print('Connecting to server.')
try:
  sio.connect('http://localhost:3000')
except socketio.exceptions.ConnectionError as err:
  print("Error Connecting to Server:\n", err)
  exit()
else:
  print('Connection to server established.')

print("Reading %s." % sys.argv[1])

tree = ET.parse(sys.argv[1])
root = tree.getroot()

trkpts = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
updates = [{'lat': trkpt.get('lat'), 'lon': trkpt.get('lon')} for trkpt in trkpts]

times = root.findall('.//{http://www.topografix.com/GPX/1/1}time')[1:]
parsed_times = [datetime.strptime(time.text, '%Y-%m-%dT%H:%M:%SZ') for time in times]

print("Streaming %d track points to the server." % len(trkpts))

index = 0

while index < len(trkpts) - 1:
  sio.emit('updateGps', updates[index])
  print("Update %d of %d sent." % (index, len(trkpts)), end='\r')

  time.sleep((parsed_times[index + 1] - parsed_times[index]).total_seconds())
  index += 1

sio.emit('updateGps', updates[index])
print("Update %d of %d sent." % (index, len(trkpts)))