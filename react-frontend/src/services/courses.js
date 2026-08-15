import api from './api';

export const getCourses = async () => {
  try {
    const response = await api.get('/api/courses');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to fetch courses' };
  }
};

export const getCourse = async (id) => {
  try {
    const response = await api.get(`/api/courses/${id}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to fetch course' };
  }
};

export const searchCourses = async (query, domain, level, price) => {
  try {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (domain && domain !== 'all') params.append('domain', domain);
    if (level && level !== 'all') params.append('level', level);
    if (price && price !== 'all') params.append('price', price);
    
    const response = await api.get(`/api/courses/search?${params.toString()}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Search failed' };
  }
};

export const getRecommendations = async () => {
  try {
    const response = await api.get('/api/courses/recommend');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to fetch recommendations' };
  }
};

export const createCourse = async (courseData) => {
  try {
    const response = await api.post('/api/courses', courseData);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to create course' };
  }
};