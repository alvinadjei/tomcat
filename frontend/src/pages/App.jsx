import '../static/App.css';
import { Link } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';

function App() {

  const [_, setMotionDetected] = useState(false);
  const previousMotion = useRef(false);
  const audioRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:5000/motion');
        const data = await res.json();

        if (data.motion && !previousMotion.current) {
          // Motion just started
          if (audioRef.current) {
            audioRef.current.currentTime = 0;
            audioRef.current.play();
          }
        } else if (!data.motion && previousMotion.current) {
          // Motion just stopped
          if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
          }
        }

        previousMotion.current = data.motion;
        setMotionDetected(data.motion);
      } catch (error) {
        console.error('Error fetching motion status:', error);
      }
    }, 500); // Check every 0.5s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <h1>Mouse Cam</h1>
      {/* Hidden audio element */}
      <audio ref={audioRef} src="/alert.mp3" preload="auto" loop />
      <img
        src="http://localhost:5000/video"
        alt="Mouse Cam"
        style={{ width: '60%', border: '2px solid #ccc' }}
      />
      <br />
      <Link to="/recordings">
        <button> {/* style={{ marginTop: '20px', padding: '10px 20px', fontSize: '16px' }} */}
          View Recordings
        </button>
      </Link>
      <br />
      <button onClick={() => audioRef.current?.play()}>
        Enable Sound
      </button>
    </div>
  );
}

export default App;
