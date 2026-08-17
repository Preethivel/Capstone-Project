import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated, isLearner, isInstructor, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md py-3 px-6 flex justify-between items-center">
      <div className="flex items-center space-x-6">
        <Link to="/" className="text-xl font-bold text-blue-600">
          LearnVerse
        </Link>
        <Link to="/" className="text-gray-700 hover:text-blue-600">Home</Link>
        <Link to="/courses" className="text-gray-700 hover:text-blue-600">Courses</Link>
        
        {isAuthenticated && isLearner && (
          <Link to="/dashboard" className="text-gray-700 hover:text-blue-600">My Dashboard</Link>
        )}
        
        {isAuthenticated && isInstructor && (
          <>
            <Link to="/instructor/dashboard" className="text-gray-700 hover:text-blue-600">Instructor</Link>
            <Link to="/instructor/course/create" className="text-gray-700 hover:text-blue-600">Create Course</Link>
          </>
        )}
        
        {isAuthenticated && isAdmin && (
          <Link to="/admin" className="text-gray-700 hover:text-blue-600">Admin Panel</Link>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {isAuthenticated ? (
          <>
            <span className="text-sm text-gray-600">
              👤 {user?.name} ({user?.role})
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="text-sm text-blue-600 hover:text-blue-800">Login</Link>
            <Link to="/signup" className="text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;