from pyrplidar import PyRPlidar
import threading
from queue import Queue
import time
import socketio
import math
from statistics import mean
import numpy as np
import cv2
from kalmanfilter import KalmanFilter_2d, KalmanFilter_1d

# list of ports to which the lidar sensors are conneted
# RPILIDAR Ports:
# Linux   : "/dev/ttyUSB0"
# MacOS   : "/dev/cu.SLAB_USBtoUART"
# Windows : "COM5"

# Each sensor needs a port, x,y position (mm) in the real world and rotation angle (degrees)
sensors_config = [
    {
        "port": "/dev/ttyUSB0",
        "x": 0,
        "y": -270,
        "a": 270,
        "h": "high"
    },
    {
        "port": "/dev/ttyUSB1",
        "x": 1355,
        "y": -270,
        "a": 90,
        "h": "low"
    },    
    {  
        "port": "/dev/ttyUSB2",
        "x": 1355,
        "y": 1060,
        "a": 270,
        "h": "high"
    },
    {   
        "port": "/dev/ttyUSB3",
        "x": 0,
        "y": 1060,
        "a": 90,
        "h": "low"
    }  
]

# area of interes (actual screen/step-area size in mm) coordinates
aoi_coordinates = ((0,0),(1185,660))

sio = socketio.Client()
data_send_ferq = 0.1 #how often to send the data to the server (seconds)

# the scale is to convert real world dimentions to screen Pixels
# to determine the scaling, set the margin to 0
# place an object at the bottom right corner of the screen
# in the front-end click in the center of the detected object
# devide the "X" coordinate by 100 and miltiply by the current scale 
# komaba setup scale - 11.7
# kashiwa setup scale - 13.1
# debug scale=30 margin=500
scale = 11.7
# use this in combinaion with scale to show objects which would usually appear off screen
margin = -20

# Threads stopping event
stop_event = threading.Event()

class lidarReaderThread(threading.Thread):
    def __init__(self, sensor_port, pos_x, pos_y, pos_r, pos_h, stop_event):
        
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
        self.sensor_height = pos_h

        # inti LIDAR sensor
        try:
            self.sensor_port = sensor_port
            self.lidar = PyRPlidar()
            self.lidar.connect(port=self.sensor_port, baudrate=115200, timeout=3)
            self.lidar.set_motor_pwm(500)    
            time.sleep(2)
        except Exception as e:
            print(f"Could not init the sensor on {self.sensor_port}... {e}")


    def run(self):
        
        global sio
        try:
            scan_generator = self.lidar.force_scan()
            print(f"LIDAR {self.sensor_port} is Scanning...")

            for count, scan in enumerate(scan_generator()):
                
                # Get data from sensor (angle + dist) and convert to X,Y
                new_point_x = self.sensor_pos_x + scan.distance * math.sin(math.radians(scan.angle + self.sensor_rotation))
                new_point_y = self.sensor_pos_y - scan.distance * math.cos(math.radians(scan.angle + self.sensor_rotation))
                
                # TODO: the bellow solution results in lidar points ghosting which works but might need solving.
                self.points[count % len(self.points)] = [new_point_x, new_point_y]  

                if self.stop_event.is_set():
                    break

        except Exception as e:
            print(f"SOMETHING WENT WRONG! ... {e}")

        print(f"Closing connetion to LIDAR sensor on {self.sensor_port}.")

        try:
            self.lidar.stop()
            self.lidar.set_motor_pwm(0)
            self.lidar.disconnect()

        except Exception as e:
            print(f"Could not gracefully close connection with sensor on {self.sensor_port}... {e}")



def lidar_scanner():

    # event to stop the lidar threads 
    global stop_event
    prev_frame_points = np.array([], dtype=int)

    # Trajectory prediction for user position smoothing
    kf_2d = KalmanFilter_2d()
    kf_1d = KalmanFilter_1d()
    
    # Init the LIDAR sensors scan
    lidar_sensors_threads = []
    for sensor in sensors_config:        
        new_thread  = lidarReaderThread(sensor["port"], sensor["x"], sensor["y"], sensor["a"], sensor["h"] ,stop_event)
        lidar_sensors_threads.append(new_thread)
        lidar_sensors_threads[-1].start()

    try:
        while True:
            time.sleep(data_send_ferq)

            # send LIDAR data to the socket
            # for sensor_thread in lidar_sensors_threads:
            #     sensor_data = {"points": [[(p[0]+margin)/scale, (p[1]+margin)/scale] for p in sensor_thread.points], "id": sensor_thread.sensor_port}
            #     sio.emit('updatelidar', sensor_data)

            # Calculate user positions and send to socket
            user_leg_points = []
            user_foot_points = []

            for sensor_thread in lidar_sensors_threads:
                for point in sensor_thread.points:
                    if (point[0] > aoi_coordinates[0][0] and 
                        point[1] > aoi_coordinates[0][1] and 
                        point[0] < aoi_coordinates[1][0] and
                        point[1] < aoi_coordinates[1][1] ):
                        
                        if sensor_thread.sensor_height == "high":
                            user_leg_points.append(point)
                        else:
                            user_foot_points.append(point)

            
            if len(user_leg_points) > 2 and len(user_foot_points) > 2:

                user_leg_points_np = np.array(user_leg_points, dtype=int)
                user_foot_points_np = np.array(user_foot_points, dtype=int)

                #Fit an ellipse around the used points to estimate position and orientation
                foot_ellipse = cv2.minAreaRect(user_foot_points_np)
                leg_ellipse = cv2.minAreaRect(user_leg_points_np)
                # print(f"ellipse angle: {ellipse[2]}")          


                # User position and orienation estimation via NP:
                # x_points = np.array([p[0] for p in user_points])
                # y_points = np.array([p[1] for p in user_points])     

                # avg_x = np.mean(x_points) #mean([p[0] for p in user_points])
                # avg_y = np.mean(y_points) #mean([p[1] for p in user_points])
                # user_angle =  math.atan(np.polyfit(x_points, y_points, 1)[0])
                
                # get user position and orientaion via ellipse   
                avg_leg_x = leg_ellipse[0][0]
                avg_leg_y = leg_ellipse[0][1]
                avg_foot_x = foot_ellipse[0][0]
                avg_foot_y = foot_ellipse[0][1]               
                
                avg_x = (avg_foot_x + avg_leg_x) / 2
                avg_y = (avg_foot_y + avg_leg_y) / 2

                user_angle = math.atan2(avg_foot_y-avg_leg_y, avg_foot_x-avg_leg_x) #math.radians(foot_ellipse[2])

                # Smooth User Position using Kalman filter
                smooth_pos = kf_2d.predict(int(avg_x), int(avg_y))
                smooth_posx=smooth_pos[0]
                smooth_posy=smooth_pos[1]                
                
                smooth_rot = float(kf_1d.predict(user_angle))

                # Send raw position data to the server
                # sio.emit("updatepassenger",{"id": 1,"position": {"x": (avg_x + margin) / scale, "y": (avg_y + margin) / scale, "rotation": user_angle+1.57 }} )                

                # Send smoothed position data to the server
                sio.emit("updatepassenger",{"id": 1,"position": {"x": (smooth_posx + margin) / scale, "y": (smooth_posy + margin) / scale, "rotation": smooth_rot+1.57 }} )
                
                # --- OPENCV Viz ---
                # Show lidar points - Use for local lidar debug
                # img = np.zeros((1100,1600,3), np.uint8)
                
                # img = cv2.rectangle(img, aoi_coordinates[0], aoi_coordinates[1], (0,0,255),1)
                
                # for point in user_leg_points_np:
                #     point_tp = (point[0], point[1])
                #     img = cv2.circle(img, point_tp, 4, (52, 174, 235), 1)                
                
                # for point in user_foot_points_np:
                #     point_tp = (point[0], point[1])
                #     img = cv2.circle(img, point_tp, 4, (218, 136, 227), 1) 
                    
                #     # Show dead points
                #     # try:
                #     #     duplicates=(np.all(point==prev_frame_points, axis=1))
                #     #     for index in range(len(duplicates)):
                #     #         if duplicates[index]:
                #     #             point_tp = (prev_frame_points[index][0], prev_frame_points[index][1])
                #     #             img = cv2.circle(img, point_tp, 8, (0,0,255), 1)                            
                #     # except:
                #     #     pass
                #     # 
            
                # # user position and orientation
                # img = cv2.circle(img, (int(avg_x), int(avg_y)), 8, (0,255,255), 4)
                # img = cv2.line(img, (int(avg_x), int(avg_y)), ( int(avg_x + 40 * math.cos(user_angle)), int(avg_y + 30 * math.sin(user_angle))), (0,255,255), 4)         
                
                # # Smoothed Position vis
                # img = cv2.circle(img, (smooth_posx, smooth_posy), 20, (255,255,255), 2)
                # img = cv2.line(img, (smooth_posx, smooth_posy), ( int(smooth_posx + 40 * math.cos(smooth_rot)), int(smooth_posy + 30 * math.sin(smooth_rot))), (255,255,255), 8)

                # img = cv2.ellipse(img, leg_ellipse, (52, 174, 235), 2)
                # img = cv2.ellipse(img, foot_ellipse, (218, 136, 227), 2)

                # cv2.imshow("frame", img)


                # if cv2.waitKey(1) == ord('q'):
                #     stop_event.set()                    
                # ---- END of Open CV viz ----            
            
            # prev_frame_points = user_points_np
            
            if stop_event.is_set():
                    break
         
    except (KeyboardInterrupt, SystemExit):
        # stop data collection.
        stop_event.set()
    
    except Exception as e:
        print(f"Something went wrong... {e}")
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
    stop_event.set()
    print('disconnected from server')


if __name__ == "__main__":
    
    # setup socket io client
    try:
        sio.connect('https://server.rippple.link:443')        
        # sio.connect('https://rippleserver.herokuapp.com:443')
        # sio.connect('http://0.0.0.0:3000')        
    
    except Exception as e:
        print(f"SocketIO ConnectionError: {e}")
    
    else:
        print("Connected to Ripple Server!")    
        sio.emit("updatepassengerposition",{"id": 1,"position": {"x": 0, "y": 0}} )    

        lidar_scanner()    