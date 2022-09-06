#https://pysource.com/2021/10/29/kalman-filter-predict-the-trajectory-of-an-object/
import cv2
import numpy as np


class KalmanFilter_2d:
    
    systemNoiseCovIndex = 1000
    sensorNoiseCovIndex = 1000
    kf = cv2.KalmanFilter(4, 2)
        
    #Fk - State Transition/Prediction Matrix
    kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)    
    # Qk - State/Process noise covariance matrix
    # kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 1
    kf.processNoiseCov *= systemNoiseCovIndex


    #Hk Measurement
    kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    # Rk - Sesneor / Measurement Noise Covariance
    # kf.measurementNoiseCov = np.array([[1,0],[0,1]],np.float32) * 1
    kf.measurementNoiseCov *= sensorNoiseCovIndex

    def predict(self, coordX, coordY):
        ''' This function estimates the position of the object'''
        measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        x, y = int(predicted[0]), int(predicted[1])
        return x, y


class KalmanFilter_1d:
    
    systemNoiseCovIndex = 0.0003
    sensorNoiseCovIndex = 1
    kf = cv2.KalmanFilter(2, 1)
    
    kf.transitionMatrix = np.array([[1, 1], [0, 1]], np.float32)
    kf.processNoiseCov *= systemNoiseCovIndex
    # kf.processNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.001

    kf.measurementMatrix = np.array([[1, 0]], np.float32)
    kf.measurementNoiseCov *= sensorNoiseCovIndex
    # kf.measurementNoiseCov = np.array([[1]],np.float32) * 100

    def predict(self, val):
        ''' This function estimates the position of the object'''
        measured = np.array([[np.float32(val)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        x = predicted[0]
        return x
