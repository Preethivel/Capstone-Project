import { CheckCircle2, Home as HomeIcon } from 'lucide-react';
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import AdminPanel from './pages/AdminPanel';
import AiAssistant from './pages/AiAssistant';
import CourseDetail from './pages/CourseDetail';
import Courses from './pages/Courses';
import Home from './pages/Home';
import InstructorCourseManager from './pages/InstructorCourseManager';
import InstructorCreateCourse from './pages/InstructorCreateCourse';
import InstructorDashboard from './pages/InstructorDashboard';
import InstructorEditCourse from './pages/InstructorEditCourse';
import InstructorLessons from './pages/InstructorLessons';
import InstructorAnalytics from './pages/InstructorAnalytics';
import InstructorStudents from './pages/InstructorStudents';
import LearnerDashboard from './pages/LearnerDashboard';
import LessonView from './pages/LessonView';
import Login from './pages/Login';
import Payment from './pages/Payment';
import Signup from './pages/Signup';

const ResultPage = ({ success = false }) => <main className="page"><div className="container"><div className="empty-state"><div className="empty-state-icon">{success ? <CheckCircle2 size={24} /> : <HomeIcon size={24} />}</div><h3>{success ? 'You are all set.' : 'That page wandered off.'}</h3><p>{success ? 'Your course access is ready whenever you are.' : 'Let us take you somewhere useful.'}</p><Link to={success ? '/dashboard' : '/'} className="btn btn-primary" style={{ marginTop: 18 }}>{success ? 'Open dashboard' : 'Back home'}</Link></div></div></main>;

function App() {
  return <BrowserRouter><div className="app-shell"><Navbar /><div className="site-main"><Routes>
    <Route path="/" element={<Home />} /><Route path="/login" element={<Login />} /><Route path="/signup" element={<Signup />} /><Route path="/courses" element={<Courses />} /><Route path="/courses/:id" element={<CourseDetail />} /><Route path="/course/:courseId/lesson/:lessonId" element={<LessonView />} />
    <Route path="/dashboard" element={<PrivateRoute requiredRole="learner"><LearnerDashboard /></PrivateRoute>} /><Route path="/my-courses" element={<PrivateRoute requiredRole="learner"><LearnerDashboard /></PrivateRoute>} /><Route path="/ai" element={<PrivateRoute requiredRole="learner"><AiAssistant /></PrivateRoute>} />
    <Route path="/instructor/dashboard" element={<PrivateRoute requiredRole="instructor"><InstructorDashboard /></PrivateRoute>} /><Route path="/instructor/courses" element={<PrivateRoute requiredRole="instructor"><InstructorCourseManager /></PrivateRoute>} /><Route path="/instructor/course/create" element={<PrivateRoute requiredRole="instructor"><InstructorCreateCourse /></PrivateRoute>} /><Route path="/instructor/course/edit/:courseId" element={<PrivateRoute requiredRole="instructor"><InstructorEditCourse /></PrivateRoute>} /><Route path="/instructor/course/:courseId/modules" element={<PrivateRoute requiredRole="instructor"><InstructorCourseManager /></PrivateRoute>} /><Route path="/instructor/course/:courseId/lessons" element={<PrivateRoute requiredRole="instructor"><InstructorLessons /></PrivateRoute>} /><Route path="/instructor/course/:courseId/analytics" element={<PrivateRoute requiredRole="instructor"><InstructorAnalytics /></PrivateRoute>} /><Route path="/instructor/course/:courseId/students" element={<PrivateRoute requiredRole="instructor"><InstructorStudents /></PrivateRoute>} />
    <Route path="/admin/*" element={<PrivateRoute requiredRole="admin"><AdminPanel /></PrivateRoute>} /><Route path="/payment/:courseId" element={<PrivateRoute><Payment /></PrivateRoute>} /><Route path="/payment/success" element={<PrivateRoute><ResultPage success /></PrivateRoute>} /><Route path="*" element={<ResultPage />} />
  </Routes></div><footer className="footer">© 2026 LearnVerse · Learn with intention.</footer></div></BrowserRouter>;
}

export default App;
