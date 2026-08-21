import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getEnrollments } from '../services/enrollment';

const LearnerDashboard = () => {
  const { user } = useAuth();
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEnrollments();
  }, []);

  const fetchEnrollments = async () => {
    setLoading(true);
    const result = await getEnrollments();
    if (result.success) {
      setEnrollments(result.data);
    } else {
      setError('Failed to load enrollments');
    }
    setLoading(false);
  };

  // Calculate stats
  const totalCourses = enrollments.length;
  const completedCourses = enrollments.filter(e => e.progress === 100).length;
  const inProgressCourses = enrollments.filter(e => e.progress > 0 && e.progress < 100).length;
  const notStartedCourses = enrollments.filter(e => e.progress === 0).length;

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-gray-500">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
        👋 Welcome, {user?.name || 'Learner'}!
      </h1>
      <p className="text-gray-600 mb-6">Here's your learning journey so far.</p>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl font-bold text-blue-600">{totalCourses}</div>
          <div className="text-sm text-gray-500">Enrolled Courses</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl font-bold text-green-600">{completedCourses}</div>
          <div className="text-sm text-gray-500">Completed</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl font-bold text-yellow-600">{inProgressCourses}</div>
          <div className="text-sm text-gray-500">In Progress</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md text-center">
          <div className="text-3xl font-bold text-gray-600">{notStartedCourses}</div>
          <div className="text-sm text-gray-500">Not Started</div>
        </div>
      </div>

      {/* My Courses */}
      <h2 className="text-2xl font-bold text-gray-900 mb-4">📚 My Courses</h2>

      {error ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <p className="text-red-500">{error}</p>
        </div>
      ) : enrollments.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <p className="text-xl text-gray-600">You haven't enrolled in any courses yet.</p>
          <Link to="/courses" className="inline-block mt-4 text-blue-600 hover:underline">
            Browse Courses →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {enrollments.map((enrollment) => (
            <div key={enrollment.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-5">
                <h3 className="text-lg font-semibold text-gray-900">
                  {enrollment.course?.title || 'Unknown Course'}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  by {enrollment.course?.instructor || 'Unknown Instructor'}
                </p>
                
                {/* Progress Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>{enrollment.progress}% complete</span>
                    <span>
                      Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${
                        enrollment.progress === 100 ? 'bg-green-600' : 'bg-blue-600'
                      }`}
                      style={{ width: `${enrollment.progress}%` }}
                    ></div>
                  </div>
                </div>

                <Link
                  to={`/course/${enrollment.course_id}`}
                  className="mt-4 block text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  {enrollment.progress === 100 ? 'Review Course →' : 'Continue Learning →'}
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearnerDashboard;