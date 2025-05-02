from flask import Flask, Response, render_template
import numpy as np
import cv2

app = Flask(__name__)

# Open a connection to the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)
ret, prev_frame = cap.read()
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

def generate_frames():
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
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

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)