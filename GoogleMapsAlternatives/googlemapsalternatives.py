import googlemaps
import numpy as np
import socketio

gmaps = googlemaps.Client(key='AIzaSyDZ-f76t7NJILMGk6OAzIfXh12HlcuEzc4')

sio = socketio.Client()

print('Connecting to server.')
try:
  sio.connect('https://rippleserver.herokuapp.com:443')
except socketio.exceptions.ConnectionError as err:
  print("Error Connecting to Server:\n", err)
  exit()
else:
  print('Connection to server established.')

  print('Waiting to receive state.')

alternatives = []

@sio.on('state')
def on_state(state):
    print('Received state, getting distance_matricies.')

    origins = [{'lat': stop['lat'], 'lng': stop['lon']} for stop in state['route']]

    for (i, o) in enumerate(origins[:-1]):
        destinations = origins[(i + 1):]

        walking_distance_matrix = gmaps.distance_matrix(o, destinations, mode="walking")
        walking_distances = [[{'icon': 'person-walking', 'eta': e['duration']['value'] // 60 + 1}] if e['status'] == 'OK' else [] for e in walking_distance_matrix['rows'][0]['elements']]


        bicycling_distance_matrix = gmaps.distance_matrix(o, destinations, mode="bicycling")
        bicycling_distances = [[{'icon': 'person-biking', 'eta': e['duration']['value'] // 60 + 1}] if e['status'] == 'OK' else [] for e in bicycling_distance_matrix['rows'][0]['elements']]

        driving_distance_matrix = gmaps.distance_matrix(o, destinations, mode="driving")
        driving_distances = [[{'icon': 'car', 'eta': e['duration']['value'] // 60 + 1}] if e['status'] == 'OK' else [] for e in driving_distance_matrix['rows'][0]['elements']]

        transit_distance_matrix = gmaps.distance_matrix(o, destinations, mode="transit")
        transit_distances = [[{'icon': 'train-subway', 'approximate': True, 'eta': e['duration']['value'] // 60 + 1}] if e['status'] == 'OK' else [] for e in transit_distance_matrix['rows'][0]['elements']]

        alternatives.append([[]] * (i + 1) + [walking_distances[i] + bicycling_distances[i] + driving_distances[i] + transit_distances[i] for (i, _) in enumerate(walking_distances)])

    print('Updating state.')
    sio.emit('updatealternatives', alternatives)

    print('Update completed, disconnecting.')
    sio.disconnect()
