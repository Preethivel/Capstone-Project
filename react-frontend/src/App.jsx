import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from './services/api';
import Login from './pages/Login';
import Signup from './pages/Signup';
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

        {/* Navigation Links */}
        <div className="text-center mt-4 space-x-4">
          <Link to="/" className="text-blue-600 hover:underline">🏠 Home</Link>
          <Link to="/login" className="text-blue-600 hover:underline">🔐 Login</Link>
          <Link to="/signup" className="text-blue-600 hover:underline">📝 Signup</Link>
          <Link to="/courses" className="text-blue-600 hover:underline">📚 Courses</Link>
          <Link to="/dashboard" className="text-blue-600 hover:underline">📊 Dashboard</Link>
        </div>

        <div className="text-center mt-8 text-sm text-gray-500">
          FastAPI Backend → Port 8000 | React Frontend → Port 5173
        </div>

        <Routes>
          <Route path="/" element={<div className="text-center mt-10 text-xl text-gray-700">🏠 Homepage</div>} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/courses" element={<div className="text-center mt-10 text-xl text-gray-700">📚 Courses Page</div>} />
          <Route path="/course/:id" element={<div className="text-center mt-10 text-xl text-gray-700">📖 Course Detail</div>} />
          <Route path="/dashboard" element={<div className="text-center mt-10 text-xl text-gray-700">📊 Dashboard</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;