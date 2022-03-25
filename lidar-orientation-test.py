import cv2
import numpy as np

image = np.ones((1000,1000,3), np.uint8)
window_name = 'image'

# raw_pts = [ [100,100], [200,200], [300,300], [300,400], [400,300], [250,260], [100,100], [100, 150], [240,280] ]
points =  np.random.randint(10,500, size=(8,2), dtype=int)
# points =  np.array(raw_pts)
for point in points:
    image = cv2.circle(image, point, 6, (255,255,255), 1)    

ellipse = cv2.fitEllipse(points)
image = cv2.ellipse(image, ellipse, (0,255,0), 2)


cv2.imshow(window_name, image)  
cv2.waitKey(0) 
cv2.destroyAllWindows() 
