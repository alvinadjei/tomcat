// // src/Videos.jsx
// import { useEffect, useState } from 'react'
// import { createClient } from '@supabase/supabase-js'

// const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_KEY)

// export default function Videos() {
//   const [videos, setVideos] = useState([])

//   useEffect(() => {
//     async function fetchVideos() {
//       const { data, error } = await supabase.storage
//         .from('videos')
//         .list('', { limit: 100, sortBy: { column: 'created_at', order: 'desc' } })

//       if (error) {
//         console.error('Error fetching videos:', error)
//       } else {
//         setVideos(data)
//       }
//     }

//     fetchVideos()
//   }, [])

//   const getVideoUrl = (filename) =>
//     `${import.meta.env.VITE_SUPABASE_URL}/storage/v1/object/public/videos/${filename}`

//   return (
//     <div>
//       <h1>Saved Videos</h1>
//       <a href="/">← Back to Live Feed</a>
//       <ul>
//         {videos.map((video) => (
//           <li key={video.name}>
//             <a href={getVideoUrl(video.name)} target="_blank" rel="noreferrer">
//               {video.name}
//             </a>
//           </li>
//         ))}
//       </ul>
//     </div>
//   )
// }
