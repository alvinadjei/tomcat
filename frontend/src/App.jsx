import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Mouse Cam</h1>
      <img
        src="http://localhost:5000/video"
        alt="Mouse Cam"
        style={{ width: '60%', border: '2px solid #ccc' }}
      />
    </div>
  );
}

export default App;
