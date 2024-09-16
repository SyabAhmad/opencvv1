import cv2

image = cv2.imread(r"I:\Code\opencv\denoising images\image\image1.jpeg")


if image is None:
    print("Problem loading image")
else:
    # to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gaussian blur
    # image = cv2.GaussianBlur(image,(3,3),0)
    
    # Median Blur
    # image = cv2.medianBlur(image, 3)
    
    # Bilateral Filter
    image = cv2.bilateralFilter(image, 9, 75, 75)
    
    cv2.imshow("Profile Imagee", image)
    
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()