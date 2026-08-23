import React from 'react';
import { useParams } from 'react-router-dom';

const InstructorEditCourse = () => {
  const { courseId } = useParams();
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Edit Course #{courseId}</h1>
      <div className="bg-white rounded-xl shadow-sm p-6">
        <p className="text-gray-500">Course edit form coming soon...</p>
        <p className="text-sm text-gray-400 mt-2">Course ID: {courseId}</p>
      </div>
    </div>
  );
};

export default InstructorEditCourse;