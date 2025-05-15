import { FaArrowLeft } from 'react-icons/fa'; // Font Awesome
import '../static/Recordings.css';
import { Link } from 'react-router-dom';
import RecordingDownload from '../components/RecordingDownload';
import { useEffect, useState } from "react";
import { supabase } from '../lib/supabaseClient';


const BUCKET = 'recordings';
const FOLDER = 'recordings';

export default function Recordings() {
  const [recordings, setRecordings] = useState([]);

  useEffect(() => {
    const fetchRecordings = async () => {
      
      const { data, error } = await supabase.storage
        .from(BUCKET)
        .list(FOLDER, {
          limit: 100,
          sortBy: { column: 'created_at', order: 'desc' },
        });

      if (error) {
        console.error('Error fetching recordings:', error);
      } else {
        setRecordings(data);
      }
    };

    fetchRecordings();
  }, []);

  return (
    <>
      <Link to="/" style={{ display: 'flex', justifyContent: 'flex-start' }}>
        <FaArrowLeft size={24} color='white' />
      </Link>
      <h1>Recordings</h1>
      <ul className='video-grid'>
        {recordings.map((recording) => (
                    <li key={recording.name}>
                        <RecordingDownload videoName={recording.name} />
                    </li>
                ))}
      </ul>
    </>
  );
}