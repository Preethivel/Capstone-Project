import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from './services/api';
import './App.css';

function App() {
  const [status, setStatus] = useState('Loading...');

  useEffect(() => {
    api.get('/health')
      .then(response => {
        console.log('✅ Backend connected:', response.data);
        setStatus('✅ Connected to FastAPI Backend');
      })
      .catch(error => {
        console.error('❌ Backend error:', error);
        setStatus('❌ Backend not reachable. Make sure FastAPI is running on port 8000');
      });
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 p-10">
        <h1 className="text-3xl font-bold text-center text-blue-600">
          🚀 LearnVerse React Frontend
        </h1>
        <p className="text-center text-gray-600 mt-4">{status}</p>
        <div className="text-center mt-8 text-sm text-gray-500">
          FastAPI Backend → Port 8000 | React Frontend → Port 5173
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;