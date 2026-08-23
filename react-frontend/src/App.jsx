import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import api from './services/api';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Home from './pages/Home';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import LearnerDashboard from './pages/LearnerDashboard';
import LessonView from './pages/LessonView';
import InstructorCreateCourse from './pages/InstructorCreateCourse';
import InstructorDashboard from './pages/InstructorDashboard';
import InstructorEditCourse from './pages/InstructorEditCourse';
import InstructorCourseManager from './pages/InstructorCourseManager';
import AdminPanel from './pages/AdminPanel';
import Payment from './pages/Payment';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import './App.css';

function App() {
  const [status, setStatus] = useState('Loading...');
  const [backendInfo, setBackendInfo] = useState(null);

  useEffect(() => {
    // Check backend health
    api.get('/health')
      .then(response => {
        console.log('✅ Backend connected:', response.data);
        setStatus('✅ Connected to FastAPI Backend');
        setBackendInfo(response.data);
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
          {backendInfo && (
            <p className="text-center text-xs text-gray-400 mt-1">
              API Version: {backendInfo.version || '1.0.0'} | Status: {backendInfo.status || 'OK'}
            </p>
          )}
          <div className="text-center mt-8 text-sm text-gray-500">
            FastAPI Backend → Port 8000 | React Frontend → Port 5173
          </div>

          <Routes>
            {/* ==================== PUBLIC ROUTES ==================== */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/courses/:id" element={<CourseDetail />} />
            <Route path="/course/:courseId/lesson/:lessonId" element={<LessonView />} />
            
            {/* ==================== LEARNER ROUTES ==================== */}
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute requiredRole="learner">
                  <LearnerDashboard />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/my-courses" 
              element={
                <PrivateRoute requiredRole="learner">
                  <LearnerDashboard />
                </PrivateRoute>
              } 
            />

            {/* ==================== INSTRUCTOR ROUTES ==================== */}
            <Route 
              path="/instructor/dashboard" 
              element={
                <PrivateRoute requiredRole="instructor">
                  <InstructorDashboard />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/instructor/courses" 
              element={
                <PrivateRoute requiredRole="instructor">
                  <InstructorCourseManager />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/instructor/course/create" 
              element={
                <PrivateRoute requiredRole="instructor">
                  <InstructorCreateCourse />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/instructor/course/edit/:courseId" 
              element={
                <PrivateRoute requiredRole="instructor">
                  <InstructorEditCourse />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/instructor/course/:courseId/modules" 
              element={
                <PrivateRoute requiredRole="instructor">
                  <InstructorCourseManager />
                </PrivateRoute>
              } 
            />

            {/* ==================== ADMIN ROUTES ==================== */}
            <Route 
              path="/admin" 
              element={
                <PrivateRoute requiredRole="admin">
                  <AdminPanel />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/admin/dashboard" 
              element={
                <PrivateRoute requiredRole="admin">
                  <AdminPanel />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/admin/users" 
              element={
                <PrivateRoute requiredRole="admin">
                  <AdminPanel />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/admin/courses" 
              element={
                <PrivateRoute requiredRole="admin">
                  <AdminPanel />
                </PrivateRoute>
              } 
            />

            {/* ==================== PAYMENT ROUTES ==================== */}
            <Route 
              path="/payment/:courseId" 
              element={
                <PrivateRoute>
                  <Payment />
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/payment/success" 
              element={
                <PrivateRoute>
                  <div className="text-center mt-20">
                    <div className="text-green-500 text-6xl mb-4">✅</div>
                    <h2 className="text-2xl font-bold text-gray-800">Payment Successful!</h2>
                    <p className="text-gray-600 mt-2">You have been enrolled in the course.</p>
                    <button 
                      onClick={() => window.location.href = '/dashboard'}
                      className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Go to Dashboard
                    </button>
                  </div>
                </PrivateRoute>
              } 
            />
            
            <Route 
              path="/payment/cancel" 
              element={
                <PrivateRoute>
                  <div className="text-center mt-20">
                    <div className="text-red-500 text-6xl mb-4">❌</div>
                    <h2 className="text-2xl font-bold text-gray-800">Payment Cancelled</h2>
                    <p className="text-gray-600 mt-2">Your payment was not completed.</p>
                    <button 
                      onClick={() => window.location.href = '/courses'}
                      className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Browse Courses
                    </button>
                  </div>
                </PrivateRoute>
              } 
            />

            {/* ==================== 404 NOT FOUND ==================== */}
            <Route 
              path="*" 
              element={
                <div className="text-center mt-20">
                  <h1 className="text-6xl font-bold text-gray-300">404</h1>
                  <h2 className="text-2xl font-semibold text-gray-700 mt-4">Page Not Found</h2>
                  <p className="text-gray-500 mt-2">The page you're looking for doesn't exist.</p>
                  <button 
                    onClick={() => window.location.href = '/'}
                    className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Go Home
                  </button>
                </div>
              } 
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;