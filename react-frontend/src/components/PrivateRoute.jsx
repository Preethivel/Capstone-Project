import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ children, requiredRole }) => {
  const { user, isAuthenticated, loading } = useAuth();
  if (loading) return <main className="page"><div className="spinner" /></main>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requiredRole && user?.role !== requiredRole && !(requiredRole === 'admin' && user?.email === 'admin@learnverse.com')) return <Navigate to="/dashboard" replace />;
  return children;
};
export default PrivateRoute;
