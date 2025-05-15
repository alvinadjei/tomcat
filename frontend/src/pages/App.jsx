import '../static/App.css';
import { Link } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <h1>Mouse Cam</h1>
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
    </div>
  );
}

export default App;
