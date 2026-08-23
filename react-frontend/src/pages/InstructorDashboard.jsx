import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { instructorService } from '../services/instructor';

const InstructorDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total_courses: 0,
    total_students: 0,
    total_revenue: 0,
    average_rating: 0,
    recent_enrollments: 0,
    courses: []
  });
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get stats - NOW USING instructorService
      const statsResponse = await instructorService.getStats();
      console.log('Stats response:', statsResponse.data);
      
      // Get courses - NOW USING instructorService
      const coursesResponse = await instructorService.getCourses();
      console.log('Courses response:', coursesResponse.data);
      
      setStats(statsResponse.data);
      setCourses(coursesResponse.data);
      
    } catch (error) {
      console.error('Error loading dashboard:', error);
      
      if (error.response) {
        if (error.response.status === 401) {
          setError('Please login again. Your session may have expired.');
        } else if (error.response.status === 403) {
          setError('You do not have permission to access this page.');
        } else if (error.response.status === 404) {
          setError('Dashboard endpoint not found. Please check if the backend is running.');
        } else {
          setError(`Server error: ${error.response.status}`);
        }
      } else if (error.request) {
        setError('Cannot connect to backend. Make sure the server is running on port 8000.');
      } else {
        setError(`Error: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCourse = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      return;
    }
    
    try {
      await instructorService.deleteCourse(courseId);
      await loadDashboardData();
      alert('✅ Course deleted successfully!');
    } catch (error) {
      console.error('Error deleting course:', error);
      alert('Failed to delete course. Please try again.');
    }
  };

  const StatCard = ({ label, value, subtext, icon, color }) => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <span className="text-white text-xl">{icon}</span>
        </div>
      </div>
    </div>
  );

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-red-700 mb-2">Something went wrong</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={loadDashboardData}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              🔄 Retry
            </button>
            <Link
              to="/"
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              🏠 Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">👨‍🏫 Instructor Dashboard</h1>
          <p className="text-gray-500 mt-1">Manage your courses and track student progress</p>
          {user && (
            <p className="text-sm text-gray-400 mt-1">
              Welcome back, {user.name || user.email}!
            </p>
          )}
        </div>
        <button
          onClick={() => navigate('/instructor/course/create')}
          className="mt-4 sm:mt-0 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-md hover:shadow-lg"
        >
          <span className="text-lg">➕</span> Create New Course
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          label="Total Courses"
          value={stats.total_courses || 0}
          subtext={`${courses.length} active courses`}
          color="bg-blue-500"
          icon="📚"
        />
        <StatCard
          label="Total Students"
          value={stats.total_students || 0}
          subtext={`${stats.recent_enrollments || 0} new in last 7 days`}
          color="bg-green-500"
          icon="👥"
        />
        <StatCard
          label="Total Revenue"
          value={`₹${stats.total_revenue || 0}`}
          subtext="Lifetime earnings"
          color="bg-purple-500"
          icon="💰"
        />
        <StatCard
          label="Average Rating"
          value={stats.average_rating || 0}
          subtext="Across all courses"
          color="bg-yellow-500"
          icon="⭐"
        />
      </div>

      {/* Course List */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">📋 Your Courses</h2>
          <span className="text-sm text-gray-500">{courses.length} courses</span>
        </div>
        
        {courses.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
            <span className="text-6xl block mb-4">📚</span>
            <p className="text-gray-500 text-lg">You haven't created any courses yet</p>
            <p className="text-sm text-gray-400 mt-2">Start sharing your knowledge with the world!</p>
            <button
              onClick={() => navigate('/instructor/course/create')}
              className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Create Your First Course
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        course.level?.toLowerCase() === 'beginner' ? 'bg-green-100 text-green-700' :
                        course.level?.toLowerCase() === 'intermediate' ? 'bg-yellow-100 text-yellow-700' :
                        course.level?.toLowerCase() === 'advanced' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {course.level || 'All Levels'}
                      </span>
                      <span className="text-sm text-gray-500">{course.domain || 'General'}</span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        course.status === 'active' ? 'bg-green-100 text-green-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {course.status || 'Active'}
                      </span>
                    </div>
                    
                    <h3 className="text-xl font-semibold text-gray-900">{course.title}</h3>
                    <p className="text-gray-600 text-sm mt-1 line-clamp-2">{course.description}</p>
                    
                    <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500">
                      <span className="flex items-center gap-1">👥 {course.students || 0} students</span>
                      <span className="flex items-center gap-1">⭐ {course.rating || 0}</span>
                      <span className="flex items-center gap-1">📖 {course.lessons_count || 0} lessons</span>
                      <span className="font-medium text-gray-900">
                        {course.price === 0 ? 'Free' : `₹${course.price}`}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Link
                      to={`/courses/${course.id}`}
                      className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm"
                    >
                      👁️ View
                    </Link>
                    <Link
                      to={`/instructor/course/edit/${course.id}`}
                      className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors text-sm"
                    >
                      ✏️ Edit
                    </Link>
                    <button
                      onClick={() => handleDeleteCourse(course.id)}
                      className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/instructor/course/create"
          className="bg-blue-50 p-4 rounded-lg text-center hover:bg-blue-100 transition"
        >
          <span className="text-2xl block">➕</span>
          <span className="text-sm font-medium text-blue-700">Create Course</span>
        </Link>
        <Link
          to="/courses"
          className="bg-green-50 p-4 rounded-lg text-center hover:bg-green-100 transition"
        >
          <span className="text-2xl block">🔍</span>
          <span className="text-sm font-medium text-green-700">Browse Courses</span>
        </Link>
        <Link
          to="/"
          className="bg-purple-50 p-4 rounded-lg text-center hover:bg-purple-100 transition"
        >
          <span className="text-2xl block">🏠</span>
          <span className="text-sm font-medium text-purple-700">Go Home</span>
        </Link>
      </div>
    </div>
  );
};

export default InstructorDashboard;