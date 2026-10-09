import { ArrowUpRight, BookOpen, Star, Users } from 'lucide-react';
import { Link } from 'react-router-dom';

const CourseCard = ({ course, progress }) => {
  const price = Number(course.price || 0);
  const rating = Number(course.rating || 0);
  const palette = `course-cover c${(Number(course.id || 1) % 3) + 1}`;
  return (
    <article className="course-card">
      <div className={palette}><span className="course-domain">{course.domain || 'Learning'}</span></div>
      <div className="course-body">
        <div className="course-meta" style={{ marginTop: 0, marginBottom: 10 }}><span className="badge">{course.level || 'All levels'}</span><span>{price === 0 ? 'Free' : `₹${price}`}</span></div>
        <h3>{course.title || 'Untitled course'}</h3>
        <p className="course-description">{course.description || 'A practical course to help you build your next skill.'}</p>
        <div className="course-meta"><span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}><Users size={14} /> {course.students || 0} learners</span><span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}><Star size={14} fill="currentColor" /> {rating ? rating.toFixed(1) : 'New'}</span></div>
        {progress !== undefined && <div style={{ marginBottom: 14 }}><div className="learning-top"><span>Progress</span><span>{progress}%</span></div><div className="progress-track"><div className="progress-fill" style={{ width: `${progress}%` }} /></div></div>}
        <div className="course-footer"><span className="muted" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '.78rem' }}><BookOpen size={14} /> {course.instructor || 'LearnVerse'}</span><Link to={`/courses/${course.id}`} className="btn btn-soft">{progress !== undefined ? 'Continue' : 'View course'} <ArrowUpRight size={15} /></Link></div>
      </div>
    </article>
  );
};
export default CourseCard;
