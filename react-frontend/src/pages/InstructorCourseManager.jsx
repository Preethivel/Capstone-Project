import React from 'react';
import { useParams } from 'react-router-dom';

const InstructorCourseManager = () => {
  const { courseId } = useParams();
  
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Course Manager</h1>
      <div className="bg-white rounded-xl shadow-sm p-6">
        <p className="text-gray-500">Manage modules and lessons for course</p>
        {courseId && <p className="text-sm text-gray-400 mt-2">Course ID: {courseId}</p>}
      </div>
    </div>
  );
};

export default InstructorCourseManager;