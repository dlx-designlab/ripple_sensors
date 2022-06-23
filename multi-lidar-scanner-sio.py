from pyrplidar import PyRPlidar
import threading
from queue import Queue
import time
import socketio
import math
from statistics import mean
import numpy as np
import cv2

# list of ports to which the lidar sensors are conneted
# RPILIDAR Ports:
# Linux   : "/dev/ttyUSB0"
# MacOS   : "/dev/cu.SLAB_USBtoUART"
# Windows : "COM5"

# Each sensor needs a port, x,y position (mm) in the real world and rotation angle (degrees)
sensors_config = [
    {
        "port": "/dev/ttyUSB0",
        "x": 670,
        "y": -270,
        "a": 270
    },
    {  
        "port": "/dev/ttyUSB1",
        "x": 1355,
        "y": 1060,
        "a": 270
    },
    {   
        "port": "/dev/ttyUSB2",
        "x": 0,
        "y": 1060,
        "a": 90
    }  
]

# area of interes (actual screen/step-area size in mm) coordinates
aoi_coordinates = ((0,0),(1340,905))

sio = socketio.Client()
data_send_ferq = 0.2 #how often to send the data to the server (seconds)

# the scale is to convert real world dimentions to screen Pixels
# to determine the scaling, set the margin to 0
# place an object at the bottom right corner of the screen
# in the front-end click in the center of the detected object
# devide the "X" coordinate by 100 and miltiply by the current scale 
# komaba setup scale - 11.7
scale = 30

# use this in combinaion with scale to show objects which would usually appear off screen
margin = 500


class lidarReaderThread(threading.Thread):
    def __init__(self, sensor_port, pos_x, pos_y, pos_r, stop_event):
        
        # init the thread
        threading.Thread.__init__(self)        
        
        # an external interrupt event to stop the thread
        self.stop_event = stop_event
        
        # an arry to store all the lidar points
        self.points = [[0]*2 for i in range(360)] 

        #Lidar Postition
        self.sensor_pos_x = pos_x
        self.sensor_pos_y = pos_y
        self.sensor_rotation = pos_r

        # inti LIDAR sensor
        self.sensor_port = sensor_port
        self.lidar = PyRPlidar()
        self.lidar.connect(port=self.sensor_port, baudrate=115200, timeout=3)
        self.lidar.set_motor_pwm(500)    
        time.sleep(2)


    def run(self):
        
        global sio
        scan_generator = self.lidar.force_scan()
        print(f"LIDAR {self.sensor_port} is Scanning...")

        last_angle = 0
        for count, scan in enumerate(scan_generator()):
            
            # Get data from sensor (angle + dist) and convert to X,Y
            new_point_x = self.sensor_pos_x + scan.distance * math.sin(math.radians(scan.angle + self.sensor_rotation))
            new_point_y = self.sensor_pos_y - scan.distance * math.cos(math.radians(scan.angle + self.sensor_rotation))
            
            # TODO: the bellow solution results in lidar points ghosting which works but might need solving.
            self.points[count % len(self.points)] = [new_point_x, new_point_y]  

            if self.stop_event.is_set():
                break


        print(f"Closing connetion to LIDAR sensor on {self.sensor_port}.")

        self.lidar.stop()
        self.lidar.set_motor_pwm(0)
        self.lidar.disconnect()


def lidar_scanner():

    # event to stop the lidar threads 
    stop_event = threading.Event()
    prev_frame_points = np.array([], dtype=int)
    
    # Init the LIDAR sensors scan
    lidar_sensors_threads = []
    for sensor in sensors_config:        
        new_thread  = lidarReaderThread(sensor["port"], sensor["x"], sensor["y"], sensor["a"], stop_event)
        lidar_sensors_threads.append(new_thread)
        lidar_sensors_threads[-1].start()
    
    print("All sensors scanning! Press Ctrl-C to stop")

    try:
        while True:
            time.sleep(data_send_ferq)

            # send LIDAR data to the socket
            for sensor_thread in lidar_sensors_threads:
                sensor_data = {"points": [[(p[0]+margin)/scale, (p[1]+margin)/scale] for p in sensor_thread.points], "id": sensor_thread.sensor_port}
                sio.emit('updatelidar', sensor_data)

            # Calculate user positions and send to socket
            user_points = []
            
            for sensor_thread in lidar_sensors_threads:
                for point in sensor_thread.points:
                    if (point[0] > aoi_coordinates[0][0] and 
                        point[1] > aoi_coordinates[0][1] and 
                        point[0] < aoi_coordinates[1][0] and
                        point[1] < aoi_coordinates[1][1] ):
                        
                        user_points.append(point)
            
            if len(user_points) > 6:
                
                user_points_np = np.array(user_points, dtype=int)
                
                #Fit an ellipse around the used points to estimate position and orientation
                ellipse = cv2.minAreaRect(user_points_np)
                # print(f"ellipse angle: {ellipse[2]}")          


                # User position and orienation estimation via NP:
                x_points = np.array([p[0] for p in user_points])
                y_points = np.array([p[1] for p in user_points])     

                # avg_x = np.mean(x_points) #mean([p[0] for p in user_points])
                # avg_y = np.mean(y_points) #mean([p[1] for p in user_points])
                # user_angle =  math.atan(np.polyfit(x_points, y_points, 1)[0])
                
                # get user position and orientaion via ellipse   
                avg_x = ellipse[0][0]
                avg_y = ellipse[0][1]
                user_angle = math.radians(ellipse[2])

                sio.emit("updatepassenger",{"id": 1,"position": {"x": (avg_x + margin) / scale, "y": (avg_y + margin) / scale, "rotation": user_angle }} )
      
                
                # --- OPENCV Viz ---
                # Show lidar points
                # Use for local lidar debug
                img = np.zeros((1100,1600,3), np.uint8)
                
                img = cv2.rectangle(img, aoi_coordinates[0], aoi_coordinates[1], (0,0,255),1)
                
                for point in user_points_np:
                    point_tp = (point[0], point[1])
                    img = cv2.circle(img, point_tp, 4, (255,255,255), 1)                

                    # Show dead points
                    # try:
                    #     duplicates=(np.all(point==prev_frame_points, axis=1))
                    #     for index in range(len(duplicates)):
                    #         if duplicates[index]:
                    #             point_tp = (prev_frame_points[index][0], prev_frame_points[index][1])
                    #             img = cv2.circle(img, point_tp, 8, (0,0,255), 1)                            
                    # except:
                    #     pass

                    int(avg_x) + 30 * math.cos(user_angle)
                
                # user position and orientation
                img = cv2.circle(img, (int(avg_x), int(avg_y)), 8, (0,255,255), 4)
                img = cv2.line(img, (int(avg_x), int(avg_y)), ( int(avg_x + 30 * math.cos(user_angle)), int(avg_y + 30 * math.sin(user_angle))), (0,255,255), 4)         


                img = cv2.ellipse(img, ellipse, (0,255,0), 2)

                cv2.imshow("frame", img)
                if cv2.waitKey(1) == ord('q'):
                    stop_event.set()                    
                # ---- END of Open CV viz ----            
            
            # prev_frame_points = user_points_np
         
    except (KeyboardInterrupt, SystemExit):
        # stop data collection.
        stop_event.set()    


@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    # todo: disconnect lidar sensors : set thread event > stop_event.set()
    print('disconnected from server')


if __name__ == "__main__":
    
    # setup socket io client
    sio.connect('http://localhost:3000')
    print("Connected to Ripple Server!")    
    sio.emit("updatepassengerposition",{"id": 1,"position": {"x": 0, "y": 0}} )    
    # sio.wait()

    lidar_scanner()