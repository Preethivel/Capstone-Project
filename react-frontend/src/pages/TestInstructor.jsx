import React, { useState, useEffect } from 'react';
import api from '../services/api';

const TestInstructor = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      console.log('📡 Fetching instructor courses...');
      const response = await api.get('/api/instructor/courses');
      console.log('✅ Response:', response);
      setData(response.data);
    } catch (error) {
      console.error('❌ Error:', error);
      setError(error.message);
    }
    setLoading(false);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>📊 Instructor Data</h1>
      <pre style={{ background: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default TestInstructor;