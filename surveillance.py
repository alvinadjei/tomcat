import numpy as np
import cv2

# Open a connection to the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)
ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

print(prev_gray.shape)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert the frame to grayscale for motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, gray)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    
    # Add blur and dilation to smooth out the noise
    thresh = cv2.GaussianBlur(thresh, (5,5), 0)
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Count how many pixels are "active"
    motion_score = cv2.countNonZero(thresh)
    if motion_score > 4000:  # You can tune this threshold
        cv2.putText(frame, "Motion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
    # Display the resulting frame
    cv2.imshow('Webcam Stream', frame)

    # Break the loop if the user presses the 'Escape' key
    if cv2.waitKey(1) == ord('q'):  # 27 is the ASCII code for the Escape key
        break

    # Update the previous frame
    prev_gray = gray.copy()

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()