import api from './api';

export const enrollCourse = async (courseId) => {
  try {
    const response = await api.post(`/api/enroll/${courseId}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Enrollment failed' };
  }
};

export const getEnrollments = async () => {
  try {
    const response = await api.get('/api/enrollments');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to fetch enrollments' };
  }
};

export const getEnrollment = async (enrollmentId) => {
  try {
    const response = await api.get(`/api/enroll/${enrollmentId}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to fetch enrollment' };
  }
};

export const updateProgress = async (enrollmentId, progress) => {
  try {
    const response = await api.put(`/api/enroll/${enrollmentId}/progress?progress=${progress}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, message: error.response?.data?.detail || 'Failed to update progress' };
  }
};