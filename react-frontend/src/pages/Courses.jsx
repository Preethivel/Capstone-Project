import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import CourseCard from '../components/CourseCard';
import { getCourses, searchCourses } from '../services/courses';

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    domain: 'all',
    level: 'all',
    price: 'all'
  });

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    setLoading(true);
    const result = await getCourses();
    if (result.success) {
      setCourses(result.data);
    } else {
      setError('Failed to load courses');
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    setLoading(true);
    const result = await searchCourses(
      searchQuery,
      filters.domain,
      filters.level,
      filters.price
    );
    if (result.success) {
      setCourses(result.data);
    } else {
      setError('Search failed');
    }
    setLoading(false);
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const resetFilters = () => {
    setSearchQuery('');
    setFilters({ domain: 'all', level: 'all', price: 'all' });
    loadCourses();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">📚 Browse Courses</h1>
      <p className="text-gray-600 mb-6">
        Discover courses from various domains and start learning today!
      </p>

      {/* Search & Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">🔍 Find Your Perfect Course</h2>
        
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <input
            type="text"
            placeholder="Search courses by title or instructor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            🔍 Search
          </button>
          <button
            onClick={resetFilters}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
          >
            ✖️ Clear
          </button>
        </div>

        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">📂 Domain</label>
            <select
              value={filters.domain}
              onChange={(e) => handleFilterChange('domain', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Domains</option>
              <option value="Programming">Programming</option>
              <option value="Web Development">Web Development</option>
              <option value="AI & ML">AI & ML</option>
              <option value="Data Science">Data Science</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="Cloud Computing">Cloud Computing</option>
              <option value="DevOps">DevOps</option>
              <option value="Mobile Development">Mobile Development</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">📊 Level</label>
            <select
              value={filters.level}
              onChange={(e) => handleFilterChange('level', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Levels</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">💰 Price</label>
            <select
              value={filters.price}
              onChange={(e) => handleFilterChange('price', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Prices</option>
              <option value="free">Free</option>
              <option value="paid">Paid</option>
            </select>
          </div>
        </div>
      </div>

      {/* Course Results */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading courses...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-500">{error}</p>
        </div>
      ) : courses.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <p className="text-xl text-gray-600">😕 No courses found</p>
          <p className="text-gray-500 mt-2">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Courses;