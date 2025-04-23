import numpy as np
import cv2

# Open a connection to the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Display the resulting frame
    cv2.imshow('Webcam Stream', frame)

    # Break the loop if the user presses the 'Escape' key
    if cv2.waitKey(1) == 27:  # 27 is the ASCII code for the Escape key
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()