from flask import Flask, Response, render_template
from flask_cors import CORS
from supabase import create_client
import cv2
import os
import datetime
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
load_dotenv()

# Load environment variables from .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    motion_threshold = 5  # Number of frames to trigger recording
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
        if motion_counter >= motion_threshold and not recording:
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
                
                # Upload to Supabase Storage
                with open(filename, "rb") as f:
                    file_data = f.read()
                    supabase.storage.from_("recordings").upload(f"recordings/{os.path.basename(filename)}", file_data)

                # Delete local copy
                os.remove(filename)
        
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
    """Video streaming confrirmation for debugging"""
    return {"status": "Backend running", "video_url": "/video"}

@app.route('/video')
def video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # Return the video stream as a multipart response
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)