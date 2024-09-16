import cv2
import numpy as np

image = cv2.imread(r"I:\Code\opencv\grayscaling images\image\image2.jpeg")

if image is None:
    print("There is no image selected")
else:
    
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    
    cv2.imshow("Profile Image", image)
    
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()