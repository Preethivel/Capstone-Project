import { useEffect, useState } from 'react';
import { ArrowLeft, Users, Trophy, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import api from '../services/api';

const InstructorStudents = () => {
  const { courseId } = useParams();
  const [students, setStudents] = useState([]);
  const [performance, setPerformance] = useState([]);
  const [activeTab, setActiveTab] = useState('students');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const [studentsRes, perfRes] = await Promise.all([
        api.get(`/api/instructor/courses/${courseId}/students`),
        api.get('/api/instructor/students/performance'),
      ]);
      setStudents(studentsRes.data?.data || studentsRes.data || []);
      setPerformance(perfRes.data || perfRes || []);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to load data');
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [courseId]);

  if (loading) return <main className="page"><div className="spinner" /></main>;
  if (error) return <main className="page"><div className="container"><div className="error-state"><h3>{error}</h3><Link to="/instructor/dashboard" className="btn btn-primary" style={{ marginTop: 18 }}>Back to dashboard</Link></div></div></main>;

  return (
    <main className="page">
      <div className="container">
        <Link to="/instructor/dashboard" className="nav-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <ArrowLeft size={15} /> Back to dashboard
        </Link>
        <div className="dashboard-header" style={{ marginTop: 22 }}>
          <div><span className="eyebrow">Student management</span><h1>Students & Performance</h1><p>View enrolled students and track their progress.</p></div>
        </div>

        <div style={{ display: 'flex', gap: 8, marginBottom: 22 }}>
          <button className={`btn ${activeTab === 'students' ? 'btn-primary' : 'btn-soft'}`} onClick={() => setActiveTab('students')}>
            <Users size={14} /> Enrolled Students
          </button>
          <button className={`btn ${activeTab === 'performance' ? 'btn-primary' : 'btn-soft'}`} onClick={() => setActiveTab('performance')}>
            <Trophy size={14} /> Top Performers
          </button>
        </div>

        {activeTab === 'students' && (
          <section className="panel">
            <div className="panel-head"><h2>Enrolled Students</h2><span className="badge">{students.length} students</span></div>
            {students.length === 0 ? (
              <div className="empty-state"><h3>No students yet</h3><p>Students will appear here once they enroll.</p></div>
            ) : (
              <div className="table-wrap"><table className="data-table">
                <thead><tr><th>Name</th><th>Email</th><th>Progress</th><th>Completed</th><th>Enrolled</th></tr></thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.id}>
                      <td><strong>{s.name}</strong></td>
                      <td>{s.email}</td>
                      <td><div className="progress-track" style={{ width: 100 }}><div className="progress-fill" style={{ width: `${s.progress}%` }} /></div> <span style={{ fontSize: '.82rem' }}>{s.progress}%</span></td>
                      <td>{s.completed_lessons || 0}</td>
                      <td className="muted" style={{ fontSize: '.82rem' }}>{s.enrolled_at?.slice(0, 10)}</td>
                    </tr>
                  ))}
                </tbody>
              </table></div>
            )}
          </section>
        )}

        {activeTab === 'performance' && (
          <section className="panel">
            <div className="panel-head"><h2>Top Performers</h2><span className="badge">Across all your courses</span></div>
            {performance.length === 0 ? (
              <div className="empty-state"><h3>No data yet</h3><p>Student performance data will appear once students are enrolled.</p></div>
            ) : (
              <div className="table-wrap"><table className="data-table">
                <thead><tr><th>#</th><th>Name</th><th>Average Progress</th><th>Courses</th><th>Completed</th></tr></thead>
                <tbody>
                  {performance.map((s, idx) => (
                    <tr key={s.id}>
                      <td><strong>{idx + 1}</strong></td>
                      <td><strong>{s.name}</strong><div className="muted" style={{ fontSize: '.82rem' }}>{s.email}</div></td>
                      <td><TrendingUp size={14} /> {s.average_progress}%</td>
                      <td>{s.course_count}</td>
                      <td><CheckCircle2 size={14} /> {s.completed_courses}</td>
                    </tr>
                  ))}
                </tbody>
              </table></div>
            )}
          </section>
        )}
      </div>
    </main>
  );
};

export default InstructorStudents;
