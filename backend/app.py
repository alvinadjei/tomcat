from flask import Flask, Response, render_template
from flask_cors import CORS
from supabase import create_client
import serial
import threading
import cv2
import os
import datetime
import time
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

### Global variables

# Flag to indicate if the program is running
running = True
running_lock = threading.Lock()  # In case multiple threads try to access the running variable at once

# Shared frame variable
latest_frame = None
frame_lock = threading.Lock()  # Lock for the latest frame

# Motion score variable
latest_motion_score = None
motion_score_lock = threading.Lock()  # Lock for the motion score


def serial_messages():
    """Thread to handle serial communication with Arduino."""
    # Initialize global variables
    global running
    
    # Set this to your actual port and baud rate
    SERIAL_PORT = '/dev/cu.usbmodem101'  # On Windows, use something like 'COM3'
    BAUD_RATE = 9600
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    time.sleep(2)  # Wait for the connection to establish

    last_sent = None

    while True:
        now = datetime.datetime.now()
        current_time = now.strftime('%H:%M')

        with running_lock:
            if current_time == "00:30" and last_sent != "go":
                ser.write(b'g')
                running = True
                last_sent = "go"

            elif current_time == "06:00" and last_sent != "stop":
                ser.write(b's')
                running = False
                last_sent = "stop"

        time.sleep(30)  # Wait 30 seconds before checking again    


def camera_thread():
    """Thread to handle video capture and motion detection."""
    # Initialize global variables
    global latest_frame, latest_motion_score
    
    # Create directory to save recordings   
    SAVE_DIR = "recordings"
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Keep track of the number of frames in a row with motion
    motion_counter = 0  # Number of frames with motion
    motion_threshold = 5  # Number of frames to trigger recording
    recording = False  # Flag to indicate if recording is in progress
    out = None  # VideoWriter object for saving video
    max_frames = 300  # Maximum number of frames to record, rougly 10 seconds at 30 FPS
    
    # Open a connection to the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Capture first frame for motion detection comparison
    ret, prev_frame = cap.read()
    if not ret:
        return
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    # Continuously capture frames and upload to Supabase
    while True:
        
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Flip frame horizontally
        frame = cv2.flip(frame, 1)
        
        # Save the frame to a global variable
        with frame_lock:
            latest_frame = frame.copy()
        
        # Convert the frame to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Add blur and dilation to smooth out the noise
        thresh = cv2.GaussianBlur(thresh, (5,5), 0)
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Count how many pixels are "active"
        motion_score = cv2.countNonZero(thresh)
        
        # Save the motion score to a global variable
        with motion_score_lock:
            latest_motion_score = motion_score
        
        # Start recording if motion persists
        if motion_counter >= motion_threshold and not recording:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"{timestamp}.avi")
            out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 20, (frame.shape[1], frame.shape[0]))
            recording = True
        
        with running_lock:
            is_running = running  # safely read the flag
        
        if is_running:
            # Write frame to video if recording
            if recording:
                out.write(frame)

                # Stop recording after max frames reached
                if motion_counter >= max_frames:
                    motion_counter = 0
                # Stop recording if no motion detected
                if motion_counter <= 0:
                    out.release()
                    recording = False
                    
                    # Upload to Supabase Storage
                    with open(filename, "rb") as f:
                        file_data = f.read()
                        supabase.storage.from_("recordings").upload(f"recordings/{os.path.basename(filename)}", file_data)

                    # Delete local copy
                    os.remove(filename)
        
        prev_gray = gray


def live_stream():
    """Thread to handle live video streaming."""
    
    while True:

        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is None:
            continue  # Skip if no frame is available
        
        with motion_score_lock:
            motion_score = latest_motion_score if latest_motion_score is not None else 0
        if motion_score is None:  # Skip if no motion score is available
            continue
        
        if motion_score > 4000:  # You can tune this threshold
            cv2.putText(frame, "Motion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Video streaming confrirmation for debugging"""
    return {"status": "Backend running", "video_url": "/video"}

@app.route('/video')
def video():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # Return the video stream as a multipart response
    return Response(live_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Start multiple threads for serial communication, camera stream, and background video monitoring
    threading.Thread(target=serial_messages, daemon=True).start()  # Start serial messaging in a background thread
    threading.Thread(target=camera_thread, daemon=True).start()  # Start camera stream in a background thread
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)