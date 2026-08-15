import api from './api';

export const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login', { email, password });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      message: error.response?.data?.detail || 'Login failed' 
    };
  }
};

export const signup = async (userData) => {
  try {
    const response = await api.post('/auth/signup', userData);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      message: error.response?.data?.detail || 'Signup failed' 
    };
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_data');
};