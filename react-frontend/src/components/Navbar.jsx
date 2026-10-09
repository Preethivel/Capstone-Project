import { useState } from 'react';
import { BookOpen, LogOut, Menu, Sparkles, X } from 'lucide-react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated, isLearner, isInstructor, isAdmin } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const close = () => setOpen(false);
  const handleLogout = () => { logout(); close(); navigate('/login'); };
  const linkClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`;

  return (
    <header className="topbar">
      <div className="container nav-inner">
        <Link to="/" className="brand" onClick={close} aria-label="LearnVerse home"><span className="brand-mark"><BookOpen size={18} /></span>LearnVerse</Link>
        <nav className={`nav-links${open ? ' open' : ''}`} aria-label="Main navigation">
          <NavLink to="/" className={linkClass} onClick={close}>Home</NavLink>
          <NavLink to="/courses" className={linkClass} onClick={close}>Courses</NavLink>
          {isAuthenticated && isLearner && <NavLink to="/dashboard" className={linkClass} onClick={close}>Dashboard</NavLink>}
          {isAuthenticated && isLearner && <NavLink to="/ai" className={linkClass} onClick={close}><Sparkles size={14} /> AI Assistant</NavLink>}
          {isAuthenticated && isInstructor && <NavLink to="/instructor/dashboard" className={linkClass} onClick={close}>Instructor Dashboard</NavLink>}
          {isAuthenticated && isAdmin && <NavLink to="/admin" className={linkClass} onClick={close}>Admin Dashboard</NavLink>}
        </nav>
        <div className="nav-actions">
          {isAuthenticated ? <><span className="user-pill"><span className="avatar">{user?.name?.slice(0, 1).toUpperCase() || 'L'}</span><span>{user?.name || 'Learner'}</span></span><button className="btn btn-ghost" onClick={handleLogout}><LogOut size={15} /> Log out</button></> : <><Link to="/login" className="nav-link">Sign in</Link><Link to="/signup" className="btn btn-primary">Get started</Link></>}
        </div>
        <button className="mobile-toggle" onClick={() => setOpen(!open)} aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open}>{open ? <X size={23} /> : <Menu size={23} />}</button>
      </div>
    </header>
  );
};
export default Navbar;
