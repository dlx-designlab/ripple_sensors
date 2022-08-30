#https://pysource.com/2021/10/29/kalman-filter-predict-the-trajectory-of-an-object/
import cv2
import numpy as np


class KalmanFilter:
    kf = cv2.KalmanFilter(4, 2)
    kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    
    kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.001
    # kf.measurementNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.00003    

    def predict(self, coordX, coordY):
        ''' This function estimates the position of the object'''
        measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        x, y = int(predicted[0]), int(predicted[1])
        return x, y



# class KalmanFilter_1D:
#     kf = cv2.KalmanFilter(2, 1)
#     kf.measurementMatrix = np.array([[1, 0], [0, 1]], np.float32)
#     kf.transitionMatrix = np.array([[1, 0], [0, 1]], np.float32)
#     # kf.processNoiseCov = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],np.float32) * 0.001
#     # kf.measurementNoiseCov = np.array([[1,0],[0,1]],np.float32) * 0.00003    

#     # kf.transitionMatrix = np.array([[1., 1.], [0., 1.]])
#     # kf.measurementMatrix = 1. * np.ones((1, 2))
#     # # kf.processNoiseCov = 1e-5 * np.eye(2)
#     # # kf.measurementNoiseCov = 1e-1 * np.ones((1, 1))


#     def predict(self, val):
#         ''' This function estimates the position of the object'''
#         measured = np.array([[np.float32(val)]])
#         self.kf.correct(measured)
#         predicted = self.kf.predict()
#         x = int(predicted[0])
#         return x
