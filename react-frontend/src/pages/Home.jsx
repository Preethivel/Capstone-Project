import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import CourseCard from '../components/CourseCard';
import { getCourses } from '../services/courses';

const Home = () => {
  const [featuredCourses, setFeaturedCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFeaturedCourses();
  }, []);

  const fetchFeaturedCourses = async () => {
    try {
      setLoading(true);
      const result = await getCourses();
      if (result.success) {
        // Take first 4 courses as featured
        setFeaturedCourses(result.data.slice(0, 4));
      } else {
        setError('Failed to load courses');
      }
    } catch (error) {
      setError('Error loading courses');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="text-center py-16 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl mb-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Learn Without <span className="text-blue-600">Boundaries</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Discover thousands of courses from world-class instructors. Start learning today and unlock your potential.
        </p>
        <Link
          to="/courses"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition"
        >
          Explore Courses →
        </Link>
      </div>

      {/* Featured Courses Section */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
          🔥 Featured Courses
        </h2>
        
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading courses...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-500">{error}</p>
          </div>
        ) : featuredCourses.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No courses available yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;