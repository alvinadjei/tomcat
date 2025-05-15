// src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './pages/App.jsx'
import Recordings from './pages/Recordings.jsx'
import './static/index.css'
// import Recordings from './Recordings.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/recordings" element={<Recordings />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
