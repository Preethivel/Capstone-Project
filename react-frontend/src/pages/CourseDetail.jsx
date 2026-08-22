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

  useEffect(() => {
    fetchCourse();
  }, [id]);

  const fetchCourse = async () => {
    setLoading(true);
    const result = await getCourse(id);
    if (result.success) {
      setCourse(result.data);
    } else {
      setError('Course not found');
    }
    setLoading(false);
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
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-gray-500">Loading course...</p>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-red-500">{error || 'Course not found'}</p>
        <Link to="/courses" className="block text-center text-blue-600 hover:underline mt-4">
          ← Back to Courses
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Course Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <span className="inline-block bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full mb-3">
              {course.domain}
            </span>
            {course.course_url && (
              <span className="inline-block bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full ml-2">
                🔗 External
              </span>
            )}
            <h1 className="text-3xl font-bold text-gray-900">{course.title}</h1>
            <p className="text-gray-600 mt-2">{course.description}</p>
            <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-500">
              <span>📊 Level: {course.level}</span>
              <span>⭐ Rating: {course.rating || 'New'}</span>
              <span>👨‍🏫 Instructor: {course.instructor}</span>
              <span>👨‍🎓 {course.students || 0} students</span>
            </div>
          </div>
          <div className="text-right">
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

      {/* Modules & Lessons */}
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
                    <p className="text-sm text-gray-500">{module.description}</p>
                  )}
                </div>
                {module.lessons && module.lessons.length > 0 && (
                  <ul className="divide-y divide-gray-100">
                    {module.lessons.map((lesson, lessonIdx) => (
                      <li key={lesson.id} className="px-4 py-2 hover:bg-gray-50 flex items-center">
                        <span className="text-gray-400 mr-3">📖</span>
                        <span className="text-gray-700">Lesson {lessonIdx + 1}: {lesson.title}</span>
                        {lesson.video_url && (
                          <span className="ml-auto text-xs text-blue-600">🎬 Video</span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No modules available for this course.</p>
        )}
      </div>

      <Link to="/courses" className="inline-block mt-6 text-blue-600 hover:underline">
        ← Back to Courses
      </Link>
    </div>
  );
};

export default CourseDetail;