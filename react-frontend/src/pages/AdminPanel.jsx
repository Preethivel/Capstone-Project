import { useEffect, useState } from 'react';
import { BookOpen, Check, ShieldCheck, Users, X, Plus, Trash2 } from 'lucide-react';
import api from '../services/api';

const AdminPanel = () => {
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateCourse, setShowCreateCourse] = useState(false);
  const [newCourse, setNewCourse] = useState({ title: '', description: '', domain: 'Programming', level: 'Beginner', price: 0, instructor: '' });

  const load = async () => {
    setLoading(true);
    try {
      const [statsResponse, usersResponse, coursesResponse] = await Promise.all([
        api.get('/api/admin/stats'),
        api.get('/api/admin/users'),
        api.get('/api/admin/courses'),
      ]);
      setStats(statsResponse.data || {});
      setUsers(usersResponse.data || []);
      setCourses(coursesResponse.data || []);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not load admin data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const setStatus = async (id, status) => { await api.patch(`/api/admin/courses/${id}/status?status=${status}`); load(); };

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await api.delete(`/api/admin/users/${userId}`);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
      load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Failed to delete user');
    }
  };

  const deleteCourse = async (courseId) => {
    if (!window.confirm('Are you sure you want to delete this course?')) return;
    try {
      await api.delete(`/api/admin/courses/${courseId}`);
      setCourses((prev) => prev.filter((c) => c.id !== courseId));
      load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Failed to delete course');
    }
  };

  const createCourse = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/courses', {
        ...newCourse,
        price: Number(newCourse.price) || 0,
      });
      setNewCourse({ title: '', description: '', domain: 'Programming', level: 'Beginner', price: 0, instructor: '' });
      setShowCreateCourse(false);
      load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Failed to create course');
    }
  };

  if (loading) return <main className="page"><div className="spinner" /></main>;
  if (error) return <main className="page"><div className="container"><div className="error-state"><h3>{error}</h3><button className="btn btn-primary" style={{ marginTop: 18 }} onClick={load}>Try again</button></div></div></main>;

  return (
    <main className="page">
      <div className="container">
        <div className="dashboard-header">
          <div><span className="eyebrow">Platform control</span><h1>Keep LearnVerse healthy.</h1><p>Review people, courses, and the signals that keep the learning space useful.</p></div>
          <span className="badge"><ShieldCheck size={14} /> Admin workspace</span>
        </div>

        <div className="stats-grid">
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Users</span><span className="stat-icon"><Users size={17} /></span></div><div className="stat-value">{stats.total_users || users.length}</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Courses</span><span className="stat-icon"><BookOpen size={17} /></span></div><div className="stat-value">{stats.total_courses || courses.length}</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Enrollments</span><span className="stat-icon"><Check size={17} /></span></div><div className="stat-value">{stats.total_enrollments || 0}</div></div>
          <div className="stat-card"><div className="stat-card-top"><span className="stat-label">Payments</span><span className="stat-icon">₹</span></div><div className="stat-value">₹{stats.total_revenue || 0}</div></div>
        </div>

        <div className="content-grid">
          <section className="panel">
            <div className="panel-head"><h2>Course moderation</h2><span className="badge">{courses.length} total</span></div>
            <div className="table-wrap"><table className="data-table">
              <thead><tr><th>Course</th><th>Instructor</th><th>Status</th><th>Review</th></tr></thead>
              <tbody>
                {courses.map((course) => (
                  <tr key={course.id}>
                    <td><strong>{course.title}</strong><div className="muted" style={{ marginTop: 4 }}>{course.domain}</div></td>
                    <td>{course.instructor}</td>
                    <td><span className="badge">{course.status}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                        <button className="btn btn-soft" onClick={() => setStatus(course.id, 'approved')} aria-label={`Approve ${course.title}`}>✓</button>
                        <button className="btn btn-soft" onClick={() => setStatus(course.id, 'rejected')} aria-label={`Reject ${course.title}`}>✗</button>
                        <button className="btn btn-soft" onClick={() => deleteCourse(course.id)} aria-label={`Delete ${course.title}`} style={{ color: '#dc2626' }}><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table></div>
            <div style={{ marginTop: 16 }}>
              <button className="btn btn-primary" onClick={() => setShowCreateCourse(!showCreateCourse)}><Plus size={14} /> Create course</button>
            </div>
          </section>

          {showCreateCourse && (
            <section className="panel">
              <div className="panel-head"><h2>Create Course</h2><button className="btn btn-ghost" onClick={() => setShowCreateCourse(false)}><X size={14} /></button></div>
              <form onSubmit={createCourse} style={{ display: 'grid', gap: 14, marginTop: 16 }}>
                <div><label className="field-label" htmlFor="title">Title</label><input className="input" id="title" value={newCourse.title} onChange={(e) => setNewCourse({ ...newCourse, title: e.target.value })} required /></div>
                <div><label className="field-label" htmlFor="description">Description</label><textarea className="textarea" id="description" value={newCourse.description} onChange={(e) => setNewCourse({ ...newCourse, description: e.target.value })} required /></div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
                  <div><label className="field-label" htmlFor="domain">Domain</label><select className="select" id="domain" value={newCourse.domain} onChange={(e) => setNewCourse({ ...newCourse, domain: e.target.value })}><option>Programming</option><option>Web Development</option><option>AI & ML</option><option>Data Science</option><option>Cybersecurity</option><option>Cloud Computing</option><option>DevOps</option></select></div>
                  <div><label className="field-label" htmlFor="level">Level</label><select className="select" id="level" value={newCourse.level} onChange={(e) => setNewCourse({ ...newCourse, level: e.target.value })}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
                  <div><label className="field-label" htmlFor="price">Price</label><input className="input" id="price" type="number" value={newCourse.price} onChange={(e) => setNewCourse({ ...newCourse, price: e.target.value })} /></div>
                  <div><label className="field-label" htmlFor="instructor">Instructor</label><input className="input" id="instructor" value={newCourse.instructor} onChange={(e) => setNewCourse({ ...newCourse, instructor: e.target.value })} /></div>
                </div>
                <button type="submit" className="btn btn-primary" style={{ justifySelf: 'start' }}>Create course</button>
              </form>
            </section>
          )}

          <section className="panel">
            <div className="panel-head"><h2>User Management</h2><span className="badge">{users.length} total</span></div>
            {users.length === 0 ? (
              <div className="empty-state"><h3>No users</h3></div>
            ) : (
              <div className="table-wrap"><table className="data-table">
                <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Action</th></tr></thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td><strong>{user.name}</strong></td>
                      <td>{user.email}</td>
                      <td><span className="badge">{user.role}</span></td>
                      <td><button className="btn btn-soft" onClick={() => deleteUser(user.id)} style={{ color: '#dc2626' }}><Trash2 size={14} /></button></td>
                    </tr>
                  ))}
                </tbody>
              </table></div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
};

export default AdminPanel;
