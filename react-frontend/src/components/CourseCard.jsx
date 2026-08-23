import React from 'react';
import { Link } from 'react-router-dom';

const CourseCard = ({ course }) => {
  const priceDisplay = course.price === 0 ? 'Free' : `₹${course.price}`;
  const ratingDisplay = course.rating ? `⭐ ${course.rating.toFixed(1)}` : '⭐ New';

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden border border-gray-100">
      <div className="p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded">
            {course.domain}
          </span>
          <span className="text-xs text-gray-500">
            {course.level}
          </span>
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
          {course.title}
        </h3>
        
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {course.description}
        </p>
        
        <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
          <span>👨‍🏫 {course.instructor}</span>
          <span>{ratingDisplay}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-blue-600">
            {priceDisplay}
          </span>
          <Link
            to={`/courses/${course.id}`}  // ✅ FIXED: Added 's'
            className="text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;