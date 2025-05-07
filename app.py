from flask import Flask, Response, render_template
import cv2
import os
import datetime

app = Flask(__name__)


def generate_frames():
    """Video streaming generator function."""
    # Open a connection to the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    ret, prev_frame = cap.read()
    if not ret:
        return
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    SAVE_DIR = "recordings"
    os.makedirs(SAVE_DIR, exist_ok=True)

    
    # Keep track of the number of frames in a row with motion
    motion_counter = 0  # Number of frames with motion
    recording = False  # Flag to indicate if recording is in progress
    out = None  # VideoWriter object for saving video

    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Flip frame horizontally
        frame = cv2.flip(frame, 1)
        
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
            motion_counter += 1  # Increment motion counter
        else:
            motion_counter = 0  # Reset motion counter if no motion detected
        
        # Start recording if motion persists
        if motion_counter >= 15 and not recording:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"{timestamp}.avi")
            out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 20, (frame.shape[1], frame.shape[0]))
            recording = True
            
        # Write frame to video if recording
        if recording:
            out.write(frame)

            # Stop recording after motion ends
            if motion_counter == 0:
                out.release()
                recording = False
                # save_video_metadata_to_db(filename)
        
        # Update prev_gray
        prev_gray = gray

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    # Release the webcam and close all OpenCV windows
    cap.release()


@app.route('/')
def index():
    """Video streaming home page."""
    # Render the HTML template
    return render_template('index.html')


@app.route('/video')
def video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # Return the video stream as a multipart response
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)  # host='0.0.0.0', port=5000