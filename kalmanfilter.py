#https://pysource.com/2021/10/29/kalman-filter-predict-the-trajectory-of-an-object/
import cv2
import numpy as np


class KalmanFilter:
    kf = cv2.KalmanFilter(4, 2)
    
    #Hk (State)
    kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    #Fk (Observation)
    kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    
    # Qk
    kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.001
    # Rk 
    # kf.measurementNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.0001

    def predict(self, coordX, coordY):
        ''' This function estimates the position of the object'''
        measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        x, y = int(predicted[0]), int(predicted[1])
        return x, y


class KalmanFilter_1D:
    kf = cv2.KalmanFilter(2, 1)
    
    kf.measurementMatrix = np.array([[1, 0]], np.float32)
    kf.transitionMatrix = np.array([[1, 1], [0, 1]], np.float32)
    kf.processNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.0001
    # kf.measurementNoiseCov = np.array([[1]],np.float32) * 0.00003    

    def predict(self, val):
        ''' This function estimates the position of the object'''
        measured = np.array([[np.float32(val)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        x = predicted[0]
        return x
