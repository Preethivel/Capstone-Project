import { useEffect, useState } from 'react';
import { ArrowRight, BookOpen, ChevronDown, ExternalLink, Star, Users } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCourse } from '../services/courses';
import { enrollCourse } from '../services/enrollment';
import api from '../services/api';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [course, setCourse] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [review, setReview] = useState({ rating: 5, comment: '' });

  useEffect(() => {
    Promise.all([
      getCourse(id),
      api.get(`/api/reviews/${id}`).catch(() => ({ data: { data: [] } })),
    ])
      .then(([courseResult, reviewResult]) => {
        if (courseResult.success) setCourse(courseResult.data);
        else setError(courseResult.message || 'Course not found');
        setReviews(reviewResult.data?.data || []);
      })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (isAuthenticated) {
      api.get('/api/enroll/')
        .then(({ data }) => setIsEnrolled(
          (data?.data || data || []).some((item) => item.course_id === Number(id)),
        ))
        .catch(() => {});
    }
  }, [id, isAuthenticated]);

  const enroll = async () => {
    if (!isAuthenticated) return navigate('/login');
    setBusy(true);
    const result = await enrollCourse(id);
    if (result.success) {
      setIsEnrolled(true);
      navigate('/dashboard');
    } else {
      setError(result.message || 'Enrollment failed');
    }
    setBusy(false);
  };

  const buyNow = () => {
    if (!isAuthenticated) return navigate('/login');
    navigate(`/payment/${id}`, { state: { price: Number(course.price) } });
  };

  const submitReview = async (event) => {
    event.preventDefault();
    try {
      await api.post(`/api/reviews/${id}`, review);
      const response = await api.get(`/api/reviews/${id}`);
      setReviews(response.data?.data || []);
      setReview({ rating: 5, comment: '' });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not save review');
    }
  };

  if (loading) return <main className="page"><div className="spinner" /></main>;
  if (!course || error) {
    return (
      <main className="page">
        <div className="container">
          <div className="error-state">
            <h3>{error || 'Course not found'}</h3>
            <Link to="/courses" className="btn btn-primary" style={{ marginTop: 18 }}>
              Back to courses
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <>
      <section className="detail-hero">
        <div className="container detail-layout">
          <div>
            <span className="eyebrow" style={{ color: '#91b5ff' }}>
              {course.domain || 'Learning'} · {course.level || 'All levels'}
            </span>
            <h1>{course.title}</h1>
            <p className="detail-description">{course.description}</p>
            <div className="detail-facts">
              <span><BookOpen size={15} /> By {course.instructor || 'LearnVerse instructor'}</span>
              <span><Users size={15} /> {course.students || 0} learners</span>
              <span><Star size={15} fill="currentColor" /> {course.rating ? Number(course.rating).toFixed(1) : 'New'}</span>
            </div>
          </div>
          <aside className="detail-side">
            <div className="detail-price">
              {Number(course.price || 0) === 0 ? 'Free' : `₹${course.price}`}
            </div>
            {course.course_url ? (
              <a
                className="btn btn-primary"
                style={{ width: '100%' }}
                href={course.course_url}
                target="_blank"
                rel="noreferrer"
              >
                Go to course <ExternalLink size={15} />
              </a>
            ) : isEnrolled ? (
              <Link className="btn btn-primary" style={{ width: '100%' }} to={`/courses/${course.id}`}>
                Continue learning <ArrowRight size={15} />
              </Link>
            ) : Number(course.price || 0) > 0 ? (
              <button className="btn btn-primary" style={{ width: '100%' }} onClick={buyNow}>
                Buy Now <ArrowRight size={15} />
              </button>
            ) : (
              <button className="btn btn-primary" style={{ width: '100%' }} onClick={enroll} disabled={busy}>
                {busy ? 'Enrolling...' : 'Enroll now'} <ArrowRight size={15} />
              </button>
            )}
            <p className="muted" style={{ fontSize: '.78rem', marginTop: 14, textAlign: 'center' }}>
              Learn at your own pace. Keep your progress.
            </p>
          </aside>
        </div>
      </section>
      <main className="page">
        <div className="container">
          <section className="curriculum">
            <span className="eyebrow">The path</span>
            <h2 className="section-title" style={{ marginTop: 7 }}>Course curriculum</h2>
            {course.modules?.length ? (
              <div className="curriculum-list">
                {course.modules.map((module, index) => (
                  <details className="module" key={module.id} open={index === 0}>
                    <summary>
                      <span>Module {index + 1}: {module.title}</span>
                      <ChevronDown size={17} />
                    </summary>
                    {module.lessons?.map((lesson, lessonIndex) => (
                      <Link
                        className="lesson-link"
                        key={lesson.id}
                        to={isEnrolled ? `/course/${course.id}/lesson/${lesson.id}` : '#'}
                        onClick={(event) => !isEnrolled && event.preventDefault()}
                      >
                        <span>
                          <BookOpen size={14} /> Lesson {lessonIndex + 1}: {lesson.title}
                        </span>
                        {isEnrolled && <ArrowRight size={14} />}
                      </Link>
                    ))}
                  </details>
                ))}
              </div>
            ) : (
              <div className="empty-state" style={{ marginTop: 18 }}>
                <BookOpen size={25} />
                <h3 style={{ marginTop: 12 }}>Curriculum coming soon</h3>
                <p>Lessons will appear here once the instructor publishes them.</p>
              </div>
            )}
          </section>
          <section className="panel" style={{ marginTop: 38 }}>
            <div className="panel-head">
              <h2>Reviews</h2>
              <span className="badge"><Star size={13} /> {reviews.length} reviews</span>
            </div>
            {reviews.length ? reviews.map((item) => (
              <div className="learning-row" key={item.id}>
                <strong style={{ color: '#d78a25' }}>{'★'.repeat(item.rating)}</strong>
                <p className="section-copy" style={{ marginTop: 5 }}>{item.comment}</p>
              </div>
            )) : <p className="section-copy">No reviews yet. Your experience could be the first.</p>}
            {isEnrolled && (
              <form onSubmit={submitReview} style={{ display: 'grid', gap: 12, marginTop: 22 }}>
                <label className="field-label" htmlFor="review">Share your experience</label>
                <textarea
                  id="review"
                  className="textarea"
                  value={review.comment}
                  onChange={(event) => setReview({ ...review, comment: event.target.value })}
                  required
                  placeholder="What helped you most?"
                />
                <div style={{ display: 'flex', gap: 10 }}>
                  <select
                    className="select"
                    style={{ maxWidth: 150 }}
                    value={review.rating}
                    onChange={(event) => setReview({ ...review, rating: Number(event.target.value) })}
                  >
                    <option value="5">5 stars</option>
                    <option value="4">4 stars</option>
                    <option value="3">3 stars</option>
                    <option value="2">2 stars</option>
                    <option value="1">1 star</option>
                  </select>
                  <button className="btn btn-primary">Submit review</button>
                </div>
              </form>
            )}
          </section>
        </div>
      </main>
    </>
  );
};

export default CourseDetail;
