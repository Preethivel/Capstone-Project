import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const LessonView = () => {
  const { courseId, lessonId } = useParams();
  const { user, isAuthenticated } = useAuth();
  const [lesson, setLesson] = useState(null);
  const [course, setCourse] = useState(null);
  const [allLessons, setAllLessons] = useState([]);
  const [completedLessons, setCompletedLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [markingComplete, setMarkingComplete] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);

  useEffect(() => {
    fetchLessonData();
  }, [courseId, lessonId]);

  const fetchLessonData = async () => {
    setLoading(true);
    try {
      // Fetch course
      const courseRes = await api.get(`/api/courses/${courseId}`);
      if (courseRes.data) {
        setCourse(courseRes.data);
        
        // Flatten all lessons
        const lessons = [];
        courseRes.data.modules?.forEach(module => {
          module.lessons?.forEach(lesson => {
            lessons.push({ ...lesson, moduleTitle: module.title });
          });
        });
        setAllLessons(lessons);
        
        // Find current lesson
        const currentLesson = lessons.find(l => l.id === parseInt(lessonId));
        if (currentLesson) {
          setLesson(currentLesson);
        } else {
          setError('Lesson not found');
        }
      }

      // Check if user is enrolled
      if (isAuthenticated) {
        try {
          const enrollmentsRes = await api.get('/api/enrollments');
          const enrolled = enrollmentsRes.data.some(e => e.course_id === parseInt(courseId));
          setIsEnrolled(enrolled);
        } catch (e) {
          console.log('Enrollment check failed:', e);
        }
      }

      // Fetch completed lessons
      try {
        const completionsRes = await api.get('/api/lesson-completions');
        if (completionsRes.data) {
          const completedIds = completionsRes.data.map(c => c.lesson_id);
          setCompletedLessons(completedIds);
        }
      } catch (e) {
        console.log('Completions fetch failed:', e);
      }
    } catch (error) {
      console.error('Error fetching lesson:', error);
      setError('Failed to load lesson');
    }
    setLoading(false);
  };

  const handleMarkComplete = async () => {
    // 🔒 Server-side verification
    if (!isAuthenticated) {
      alert('⚠️ Please login first');
      return;
    }

    if (!isEnrolled) {
      alert('⚠️ You must be enrolled in this course to mark lessons as complete');
      return;
    }

    setMarkingComplete(true);
    try {
      // Send request with course_id to verify enrollment
      const response = await api.post('/api/lesson-completions', {
        lesson_id: parseInt(lessonId),
        course_id: parseInt(courseId)
      });
      
      if (response.data.success) {
        setCompletedLessons([...completedLessons, parseInt(lessonId)]);
        alert('✅ Lesson marked as complete!');
      }
    } catch (error) {
      console.error('Error marking complete:', error);
      if (error.response?.status === 403) {
        alert('⚠️ You are not enrolled in this course');
      } else {
        alert('Failed to mark lesson as complete');
      }
    }
    setMarkingComplete(false);
  };

  const isLessonCompleted = (id) => completedLessons.includes(id);

  const getNextLesson = () => {
    const currentIndex = allLessons.findIndex(l => l.id === parseInt(lessonId));
    if (currentIndex < allLessons.length - 1) {
      return allLessons[currentIndex + 1];
    }
    return null;
  };

  const nextLesson = getNextLesson();

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-gray-500">Loading lesson...</p>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-red-500">{error || 'Lesson not found'}</p>
        <Link to={`/course/${courseId}`} className="block text-center text-blue-600 hover:underline mt-4">
          ← Back to Course
        </Link>
      </div>
    );
  }

  const isCompleted = isLessonCompleted(lesson.id);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold text-gray-900 mb-3">📚 Lessons</h3>
            <div className="space-y-2">
              {allLessons.map((l) => (
                <Link
                  key={l.id}
                  to={`/course/${courseId}/lesson/${l.id}`}
                  className={`block px-3 py-2 rounded-lg text-sm transition ${
                    l.id === parseInt(lessonId)
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <span className="flex items-center justify-between">
                    <span className="truncate">{l.title}</span>
                    {isLessonCompleted(l.id) && (
                      <span className="text-green-600">✅</span>
                    )}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-sm text-gray-500">
                  {course?.title} / {lesson.moduleTitle}
                </span>
                <h1 className="text-2xl font-bold text-gray-900">{lesson.title}</h1>
              </div>
              <button
                onClick={handleMarkComplete}
                disabled={markingComplete || isCompleted || !isEnrolled}
                className={`px-4 py-2 rounded-lg transition ${
                  isCompleted
                    ? 'bg-green-100 text-green-700 cursor-default'
                    : !isEnrolled
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {markingComplete ? 'Marking...' : isCompleted ? '✅ Completed' : 'Mark as Complete'}
              </button>
            </div>

            {!isEnrolled && (
              <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  🔒 You need to be enrolled in this course to mark lessons as complete.
                  <Link to={`/course/${courseId}`} className="ml-2 text-blue-600 hover:underline">
                    Enroll now →
                  </Link>
                </p>
              </div>
            )}

            {lesson.video_url && (
              <div className="mb-4 aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <iframe
                  src={lesson.video_url}
                  title={lesson.title}
                  className="w-full h-full"
                  allowFullScreen
                />
              </div>
            )}

            {lesson.content && (
              <div className="prose max-w-none">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700 whitespace-pre-wrap">{lesson.content}</p>
                </div>
              </div>
            )}

            <div className="mt-6 flex justify-between items-center">
              <Link to={`/course/${courseId}`} className="text-blue-600 hover:underline">
                ← Back to Course
              </Link>
              {nextLesson && (
                <Link
                  to={`/course/${courseId}/lesson/${nextLesson.id}`}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Next Lesson →
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonView;