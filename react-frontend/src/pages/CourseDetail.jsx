import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCourse } from '../services/courses';
import { enrollCourse } from '../services/enrollment';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [enrolling, setEnrolling] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);

  useEffect(() => {
    fetchCourse();
    checkEnrollmentStatus();
  }, [id]);

  const fetchCourse = async () => {
    setLoading(true);
    try {
      const result = await getCourse(id);
      if (result.success) {
        setCourse(result.data);
        setError('');
      } else {
        setError('Course not found');
      }
    } catch (err) {
      setError('Failed to load course. Please try again.');
      console.error('Error fetching course:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkEnrollmentStatus = async () => {
    if (!isAuthenticated) return;
    
    try {
      // You can add an API call to check enrollment status
      // For now, we'll just set it to false
      setIsEnrolled(false);
    } catch (error) {
      console.error('Error checking enrollment:', error);
    }
  };

  const handleEnroll = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setEnrolling(true);
    try {
      const result = await enrollCourse(id);
      if (result.success) {
        setIsEnrolled(true);
        alert('✅ Successfully enrolled in the course!');
        navigate('/dashboard');
      } else {
        alert(result.message || 'Enrollment failed. Please try again.');
      }
    } catch (error) {
      console.error('Enrollment error:', error);
      alert('Enrollment failed. Please try again.');
    }
    setEnrolling(false);
  };

  const handleBuy = () => {
    navigate(`/payment/${id}`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading course...</p>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8">
          <p className="text-red-500 text-lg">{error || 'Course not found'}</p>
          <Link to="/courses" className="inline-block mt-4 text-blue-600 hover:underline">
            ← Back to Courses
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Course Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between">
          <div className="flex-1">
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                {course.domain || 'Programming'}
              </span>
              <span className="inline-block bg-gray-100 text-gray-800 text-sm px-3 py-1 rounded-full">
                {course.level || 'Beginner'}
              </span>
              {course.course_url && (
                <span className="inline-block bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">
                  🔗 External
                </span>
              )}
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900">{course.title}</h1>
            <p className="text-gray-600 mt-2 text-lg">{course.description}</p>
            
            <div className="flex flex-wrap gap-6 mt-4 text-sm text-gray-500">
              <span>👨‍🏫 Instructor: {course.instructor || 'Unknown'}</span>
              <span>⭐ Rating: {course.rating ? course.rating.toFixed(1) : 'New'}</span>
              <span>👨‍🎓 {course.students || 0} students</span>
              <span>📊 Level: {course.level || 'Beginner'}</span>
            </div>
          </div>
          
          <div className="mt-4 md:mt-0 text-left md:text-right">
            <p className="text-3xl font-bold text-blue-600">
              {course.price === 0 ? 'Free' : `₹${course.price}`}
            </p>
            
            {course.course_url ? (
              <a
                href={course.course_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 inline-block bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
              >
                🔗 Go to Course →
              </a>
            ) : isEnrolled ? (
              <button
                disabled
                className="mt-2 inline-block bg-green-100 text-green-700 px-6 py-2 rounded-lg cursor-default"
              >
                ✅ Already Enrolled
              </button>
            ) : isAuthenticated ? (
              <button
                onClick={course.price === 0 ? handleEnroll : handleBuy}
                disabled={enrolling}
                className="mt-2 inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                {enrolling ? 'Processing...' : course.price === 0 ? 'Enroll Now' : 'Buy Now'}
              </button>
            ) : (
              <Link
                to="/login"
                className="mt-2 inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Login to Enroll
              </Link>
            )}
          </div>
        </div>

        {course.course_url && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 text-sm">
              📌 This course is hosted on an external platform. Click "Go to Course" to access it.
            </p>
          </div>
        )}
      </div>

      {/* Course Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">📚 Course Content</h2>
        
        {course.modules && course.modules.length > 0 ? (
          <div className="space-y-4">
            {course.modules.map((module, idx) => (
              <div key={module.id} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-800">
                    Module {idx + 1}: {module.title}
                  </h3>
                  {module.description && (
                    <p className="text-sm text-gray-500 mt-1">{module.description}</p>
                  )}
                </div>
                {module.lessons && module.lessons.length > 0 ? (
                  <ul className="divide-y divide-gray-100">
                    {module.lessons.map((lesson, lessonIdx) => (
                      <li key={lesson.id} className="px-4 py-3 hover:bg-gray-50 flex items-center">
                        <span className="text-gray-400 mr-3">📖</span>
                        <span className="text-gray-700 flex-1">
                          Lesson {lessonIdx + 1}: {lesson.title}
                        </span>
                        {lesson.video_url && (
                          <span className="text-xs text-blue-600">🎬 Video</span>
                        )}
                        {isEnrolled && (
                          <button
                            onClick={() => navigate(`/course/${course.id}/lesson/${lesson.id}`)}
                            className="ml-3 text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
                          >
                            Start
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-400 text-sm p-4">No lessons in this module</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No modules available for this course.</p>
            <p className="text-sm text-gray-400 mt-2">Content will be added soon.</p>
          </div>
        )}
      </div>

      {/* Back Button */}
      <Link to="/courses" className="inline-block mt-6 text-blue-600 hover:underline">
        ← Back to Courses
      </Link>
    </div>
  );
};

export default CourseDetail;