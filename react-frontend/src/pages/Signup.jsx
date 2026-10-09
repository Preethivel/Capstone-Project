import { useState } from 'react';
import { Eye, EyeOff, Sparkles } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import heroImage from '../assets/hero.png';

const Signup = () => {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '', role: 'learner' });
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });
  const submit = async (event) => {
    event.preventDefault();
    setError('');
    if (!form.name || !form.email || !form.password || !form.confirmPassword) return setError('Complete every field to create your account.');
    if (form.password.length < 8) return setError('Your password must be at least 8 characters.');
    if (form.password !== form.confirmPassword) return setError('Your passwords do not match.');
    setLoading(true);
    const result = await signup({ name: form.name, email: form.email, password: form.password, role: form.role });
    if (result.success) navigate('/login');
    else setError(result.message || 'We could not create your account.');
    setLoading(false);
  };
  return (
    <main className="auth-page">
      <section className="auth-art">
        <Link to="/" className="brand"><span className="brand-mark"><Sparkles size={17} /></span>LearnVerse</Link>
        <h1>Make room for a better kind of progress.</h1>
        <p>One thoughtful course, one useful lesson, one new capability at a time. Your learning space starts here.</p>
        <img src={heroImage} alt="Layered abstract learning illustration" />
      </section>
      <section className="auth-form-wrap">
        <div className="auth-card">
          <span className="eyebrow">Start learning</span>
          <h2>Create your LearnVerse account</h2>
          <p>Build your own learning rhythm and keep it going.</p>
          {error && <div className="form-message" style={{ marginTop: 22 }} role="alert">{error}</div>}
          <form className="auth-form" onSubmit={submit}>
            <div><label className="field-label" htmlFor="name">Full name</label><input className="input" id="name" name="name" value={form.name} onChange={update} placeholder="Alex Morgan" autoComplete="name" /></div>
            <div><label className="field-label" htmlFor="email">Email address</label><input className="input" id="email" name="email" type="email" value={form.email} onChange={update} placeholder="you@example.com" autoComplete="email" /></div>
            <div><label className="field-label" htmlFor="password">Password</label>
              <div className="password-wrap">
                <input className="input" id="password" name="password" type={show ? 'text' : 'password'} value={form.password} onChange={update} placeholder="At least 8 characters" autoComplete="new-password" />
                <button type="button" className="password-toggle" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
              </div>
            </div>
            <div><label className="field-label" htmlFor="confirmPassword">Confirm password</label><input className="input" id="confirmPassword" name="confirmPassword" type={show ? 'text' : 'password'} value={form.confirmPassword} onChange={update} placeholder="Repeat your password" autoComplete="new-password" /></div>
            <div><label className="field-label">I am a:</label>
              <div className="role-selector" style={{ display: 'flex', gap: 16, marginTop: 8 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                  <input type="radio" name="role" value="learner" checked={form.role === 'learner'} onChange={update} /> Student
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                  <input type="radio" name="role" value="instructor" checked={form.role === 'instructor'} onChange={update} /> Instructor
                </label>
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create account'}</button>
          </form>
          <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </section>
    </main>
  );
};
export default Signup;
