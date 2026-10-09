import { useEffect, useState } from 'react';import { ArrowLeft, BarChart3, Users, CheckCircle2, TrendingUp } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { instructorService } from '../services/instructor';

const InstructorAnalytics = () => {
  const { courseId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const { data } = await instructorService.getCourseAnalytics(courseId);
      setAnalytics(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to load analytics');
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [courseId]);

  if (loading) return <main className="page"><div className="spinner" /></main>;
  if (error) return <main className="page"><div className="container"><div className="error-state"><h3>{error}</h3><Link to="/instructor/dashboard" className="btn btn-primary" style={{ marginTop: 18 }}>Back to dashboard</Link></div></div></main>;
  if (!analytics) return null;

  return (
    <main className="page">
      <div className="container">
        <Link to="/instructor/dashboard" className="nav-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <ArrowLeft size={15} /> Back to dashboard
        </Link>
        <div className="dashboard-header" style={{ marginTop: 22 }}>
          <div><span className="eyebrow">Analytics</span><h1>Course analytics</h1><p>Track student progress, completion rates, and engagement.</p></div>
        </div>
        <div className="stats-grid">
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Total Students</span><span className="stat-icon"><Users size={18} /></span></div><div className="stat-value">{analytics.total_students || 0}</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Completion Rate</span><span className="stat-icon"><CheckCircle2 size={18} /></span></div><div className="stat-value">{analytics.completion_rate || 0}%</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Average Progress</span><span className="stat-icon"><TrendingUp size={18} /></span></div><div className="stat-value">{analytics.average_progress || 0}%</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Total Revenue</span><span className="stat-icon"><BarChart3 size={18} /></span></div><div className="stat-value">₹{analytics.total_revenue || 0}</div></div>
        </div>

        <div className="content-grid" style={{ marginTop: 30 }}>
          <section className="panel">
            <div className="panel-head"><h2>Progress Distribution</h2></div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10, textAlign: 'center', marginTop: 16 }}>
              {Object.entries(analytics.progress_distribution || {}).map(([range, count]) => (
                <div key={range} style={{ padding: 14, background: '#f7f9fd', borderRadius: 10 }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{count}</div>
                  <div className="muted" style={{ fontSize: '.78rem' }}>{range}%</div>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-head"><h2>Recent Reviews</h2><span className="badge">{analytics.total_reviews || 0} total</span></div>
            {(analytics.recent_reviews || []).length === 0 ? (
              <p className="muted" style={{ marginTop: 16 }}>No reviews yet.</p>
            ) : (
              <div style={{ marginTop: 12 }}>
                {(analytics.recent_reviews || []).map((r, idx) => (
                  <div key={idx} style={{ padding: '10px 0', borderBottom: idx < (analytics.recent_reviews?.length || 0) - 1 ? '1px solid var(--line)' : 'none' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong>{r.user_name}</strong>
                      <span>★ {r.rating}</span>
                    </div>
                    <p className="muted" style={{ fontSize: '.82rem', marginTop: 2 }}>{r.comment}</p>
                    <p className="muted" style={{ fontSize: '.75rem' }}>{r.date}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
};

export default InstructorAnalytics;
