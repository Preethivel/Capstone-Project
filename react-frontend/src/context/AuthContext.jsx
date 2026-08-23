import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Helper function to get user role from localStorage
  const getUserRole = () => {
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        const parsed = JSON.parse(userData);
        return parsed.role || 'learner';
      } catch (error) {
        console.error('Error parsing user data:', error);
        return 'learner';
      }
    }
    return 'learner';
  };

  useEffect(() => {
    // Check if user is logged in on load
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('user_data');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, user_id, user_name, user_role } = response.data;
      
      localStorage.setItem('access_token', access_token);
      const userData = {
        id: user_id,
        name: user_name,
        role: user_role || 'learner',
        email: email
      };
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      setUser(userData);
      return { success: true, user: userData };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Login failed. Please try again.' 
      };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await api.post('/auth/signup', userData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Signup failed. Please try again.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    setUser(null);
  };

  const value = {
    user,
    setUser,
    login,
    signup,
    logout,
    loading,
    isAuthenticated: !!user || !!localStorage.getItem('access_token'),
    isLearner: user?.role === 'learner' || getUserRole() === 'learner',
    isInstructor: user?.role === 'instructor' || getUserRole() === 'instructor',
    isAdmin: user?.email === 'admin@learnverse.com' || getUserRole() === 'admin'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;