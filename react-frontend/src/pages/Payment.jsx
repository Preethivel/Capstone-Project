import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

const Payment = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const res = await api.get(`/api/courses/${courseId}`);
        setCourse(res.data);
      } catch (error) {
        console.error('Error fetching course:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCourse();
  }, [courseId]);

  const handlePayment = async () => {
    try {
      // Simulate payment
      await api.post(`/api/enroll/${courseId}`);
      navigate('/payment/success');
    } catch (error) {
      console.error('Payment failed:', error);
      alert('Payment failed. Please try again.');
    }
  };

  if (loading) return <div className="text-center py-20">Loading...</div>;

  return (
    <div className="max-w-md mx-auto p-6 mt-10">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-center mb-6">Complete Payment</h2>
        <div className="border-b pb-4 mb-4">
          <h3 className="font-semibold">{course?.title}</h3>
          <p className="text-gray-600">{course?.description}</p>
          <p className="text-2xl font-bold text-blue-600 mt-2">₹{course?.price || 0}</p>
        </div>
        <button
          onClick={handlePayment}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Pay Now
        </button>
        <button
          onClick={() => navigate(-1)}
          className="w-full mt-3 py-2 text-gray-600 hover:text-gray-800"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default Payment;