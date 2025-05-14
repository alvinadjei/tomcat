import { FaArrowLeft } from 'react-icons/fa'; // Font Awesome
import './Recordings.css';
import { Link } from 'react-router-dom';

export default function Recordings() {
  return (
    <>
      <Link to="/" style={{ display: 'flex', justifyContent: 'flex-start' }}>
        <FaArrowLeft size={24} color='white' />
      </Link>
      <h1>Recordings</h1>
      <div className='video-selector'>
        <button>Sunday</button>
        <button>Monday</button>
        <button>Tuesday</button>
        <button>Wednesday</button>
        <button>Thursday</button>
        <button>Friday</button>
        <button>Saturday</button>
      </div>
    </>
  );
}