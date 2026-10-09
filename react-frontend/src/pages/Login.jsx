import { useState } from 'react';
import { Eye, EyeOff, LockKeyhole } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import heroImage from '../assets/hero.png';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const submit = async (event) => {
    event.preventDefault();
    setError('');
    if (!email || !password) { setError('Enter your email and password to continue.'); return; }
    setLoading(true);
    const result = await login(email, password);
    if (result.success) {
      const role = result.data?.user_role;
      if (role === 'instructor') navigate('/instructor/dashboard');
      else if (role === 'admin') navigate('/admin');
      else navigate('/dashboard');
    } else {
      setError(result.message || 'We could not sign you in.');
    }
    setLoading(false);
  };
  return (
    <main className="auth-page">
      <section className="auth-art">
        <Link to="/" className="brand"><span className="brand-mark"><LockKeyhole size={17} /></span>LearnVerse</Link>
        <h1>Keep your curiosity moving.</h1>
        <p>Pick up where you left off, find your next challenge, and keep building the skills that matter to you.</p>
        <img src={heroImage} alt="Layered abstract learning illustration" />
      </section>
      <section className="auth-form-wrap">
        <div className="auth-card">
          <span className="eyebrow">Welcome back</span>
          <h2>Welcome back 👋</h2>
          <p>Sign in to continue your learning journey.</p>
          {error && <div className="form-message" style={{ marginTop: 22 }} role="alert">{error}</div>}
          <form className="auth-form" onSubmit={submit}>
            <div><label className="field-label" htmlFor="email">Email address</label><input className="input" id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" autoComplete="email" /></div>
            <div><label className="field-label" htmlFor="password">Password</label>
              <div className="password-wrap">
                <input className="input" id="password" type={show ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" autoComplete="current-password" />
                <button type="button" className="password-toggle" onClick={() => setShow(!show)} aria-label={show ? 'Hide password' : 'Show password'}>{show ? <EyeOff size={18} /> : <Eye size={18} />}</button>
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Signing you in...' : 'Sign in'}</button>
          </form>
          <p className="auth-switch">Don&apos;t have an account? <Link to="/signup">Create one</Link></p>
        </div>
      </section>
    </main>
  );
};
export default Login;
