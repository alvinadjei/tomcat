import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import '../static/Recordings.css';

const BUCKET = 'recordings';
const FOLDER = 'recordings';

export default function RecordingDownload({ videoName }) {
  const [downloadUrl, setDownloadUrl] = useState(null);

  useEffect(() => {
    const fetchUrl = async () => {
      const { data, error } = supabase
        .storage
        .from(BUCKET)
        .getPublicUrl(FOLDER + '/' + videoName);

      if (error) {
        console.error("Error getting video URL:", error.message);
        return;
      }

      setDownloadUrl(data.publicUrl);
    }

    fetchUrl();
  }, [videoName]);

  return (
    <button disabled={!downloadUrl}>
      <span className="download-text">Download</span>
      <br />
      {downloadUrl ? (
        <a href={downloadUrl} download>
          {videoName}
        </a>
      ) : (
        'Loading...'
      )}
    </button>
  );
}
