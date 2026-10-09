import api from './api';

export const instructorService = {
  getStats: () => api.get('/api/instructor/dashboard/stats'),
  getCourses: () => api.get('/api/instructor/courses'),
  getCourseAnalytics: (courseId) => api.get(`/api/instructor/courses/${courseId}/analytics`),
  getCourseModules: (courseId) => api.get(`/api/instructor/courses/${courseId}/modules`),
  getCourseStudents: (courseId) => api.get(`/api/instructor/courses/${courseId}/students`),
  getStudentsPerformance: () => api.get('/api/instructor/students/performance'),
  createCourse: (data) => api.post('/api/instructor/courses', data),
  updateCourse: (courseId, data) => api.put(`/api/instructor/courses/${courseId}`, data),
  deleteCourse: (courseId) => api.delete(`/api/instructor/courses/${courseId}`),
  addModule: (courseId, data) => api.post(`/api/instructor/courses/${courseId}/modules`, data),
  addLesson: (moduleId, data) => api.post(`/api/instructor/modules/${moduleId}/lessons`, data),
  updateModule: (moduleId, data) => api.put(`/api/instructor/modules/${moduleId}`, data),
  deleteModule: (moduleId) => api.delete(`/api/instructor/modules/${moduleId}`),
  updateLesson: (lessonId, data) => api.put(`/api/instructor/lessons/${lessonId}`, data),
  deleteLesson: (lessonId) => api.delete(`/api/instructor/lessons/${lessonId}`),
};
