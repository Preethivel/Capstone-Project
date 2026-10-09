import { useEffect, useState } from 'react';
import { ArrowLeft, Save } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';

const InstructorEditCourse = () => {
  const { courseId } = useParams(); const navigate = useNavigate(); const [form, setForm] = useState(null); const [error, setError] = useState(''); const [saving, setSaving] = useState(false);
  useEffect(() => { api.get(`/api/instructor/courses/${courseId}`).then(({ data }) => setForm(data)).catch((requestError) => setError(requestError.response?.data?.detail || 'Unable to load course')); }, [courseId]);
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value }); const save = async (event) => { event.preventDefault(); setSaving(true); try { await api.put(`/api/instructor/courses/${courseId}`, { ...form, price: Number(form.price) }); navigate('/instructor/dashboard'); } catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to save course'); } finally { setSaving(false); } };
  return <main className="page"><div className="container" style={{ maxWidth: 820 }}><Link to="/instructor/dashboard" className="nav-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><ArrowLeft size={15} /> Back to dashboard</Link><div className="dashboard-header" style={{ marginTop: 22 }}><div><span className="eyebrow">Instructor studio</span><h1>Edit course</h1><p>Keep the learning path clear, focused, and current.</p></div></div>{error && <div className="form-message" style={{ marginBottom: 18 }}>{error}</div>}{form && <form className="panel" onSubmit={save} style={{ display: 'grid', gap: 18 }}>{['title', 'description', 'domain', 'level', 'price'].map((field) => <label className="field-label" key={field} htmlFor={field}>{field === 'description' ? 'Description' : field[0].toUpperCase() + field.slice(1)}<input className="input" id={field} name={field} type={field === 'price' ? 'number' : 'text'} value={form[field] ?? ''} onChange={update} required={field !== 'price'} /></label>)}<button className="btn btn-primary" disabled={saving} style={{ justifySelf: 'start' }}><Save size={16} /> {saving ? 'Saving...' : 'Save changes'}</button></form>}</div></main>;
};
export default InstructorEditCourse;
