import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from './services/api';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Home from './pages/Home';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import LearnerDashboard from './pages/LearnerDashboard';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
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
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <div className="p-4">
          <h1 className="text-3xl font-bold text-center text-blue-600">
            🚀 LearnVerse React Frontend
          </h1>
          <p className="text-center text-gray-600 mt-4">{status}</p>
          <div className="text-center mt-8 text-sm text-gray-500">
            FastAPI Backend → Port 8000 | React Frontend → Port 5173
          </div>

          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/course/:id" element={<CourseDetail />} />
            
            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <PrivateRoute>
                <LearnerDashboard />
              </PrivateRoute>
            } />
            
            <Route path="/instructor/dashboard" element={
              <PrivateRoute requiredRole="instructor">
                <div className="text-center mt-10 text-xl text-gray-700">👨‍🏫 Instructor Dashboard</div>
              </PrivateRoute>
            } />
            
            <Route path="/instructor/course/create" element={
              <PrivateRoute requiredRole="instructor">
                <div className="text-center mt-10 text-xl text-gray-700">📝 Create Course</div>
              </PrivateRoute>
            } />
            
            <Route path="/admin" element={
              <PrivateRoute requiredRole="admin">
                <div className="text-center mt-10 text-xl text-gray-700">⚙️ Admin Panel</div>
              </PrivateRoute>
            } />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;