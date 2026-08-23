import React from 'react';

const AdminPanel = () => {
  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">⚙️ Admin Panel</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold">Users</h3>
          <p className="text-2xl font-bold text-blue-600">0</p>
          <p className="text-sm text-gray-500">Total registered users</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold">Courses</h3>
          <p className="text-2xl font-bold text-green-600">0</p>
          <p className="text-sm text-gray-500">Total courses</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="font-semibold">Revenue</h3>
          <p className="text-2xl font-bold text-purple-600">₹0</p>
          <p className="text-sm text-gray-500">Total revenue</p>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;