import { useEffect, useState } from 'react';
import { ArrowRight, Brain, ChartNoAxesCombined, Compass, PlayCircle, Sparkles, Trophy } from 'lucide-react';
import { Link } from 'react-router-dom';
import CourseCard from '../components/CourseCard';
import { getCourses } from '../services/courses';
import heroImage from '../assets/hero.png';

const features = [
  { icon: <Compass size={21} />, tone: 'blue', title: 'Learn from Expert Courses', copy: 'Discover structured courses designed to build practical skills.' },
  { icon: <ChartNoAxesCombined size={21} />, tone: 'green', title: 'Track Your Progress', copy: 'See your learning progress and continue exactly where you stopped.' },
  { icon: <Brain size={21} />, tone: 'orange', title: 'AI Learning Assistant', copy: 'Get instant help understanding lessons and difficult concepts.' },
  { icon: <Trophy size={21} />, tone: 'purple', title: 'Build Your Skills', copy: 'Complete lessons, improve your knowledge and achieve your goals.' },
];

const Home = () => {
  const [courses, setCourses] = useState([]);
  const [state, setState] = useState('loading');
  useEffect(() => { getCourses().then((result) => { setCourses((result.data || []).slice(0, 3)); setState(result.success ? 'ready' : 'error'); }); }, []);
  return <>
    <section className="hero"><div className="container hero-grid"><div><span className="eyebrow">A calmer way to learn</span><h1>Learn. <span>Grow.</span> Achieve.</h1><p className="hero-copy">LearnVerse is a personalized learning platform where students can discover courses, learn at their own pace, track their progress, and get AI-powered learning support.</p><div className="hero-actions"><Link to="/courses" className="btn btn-primary">Explore courses <ArrowRight size={17} /></Link><Link to="/signup" className="btn btn-ghost">Get started <PlayCircle size={17} /></Link></div></div><div className="hero-visual"><div className="hero-art"><img src={heroImage} alt="Abstract layered learning platform illustration" /><div className="orbit-card orbit-one"><span className="orbit-icon"><Sparkles size={16} /></span><span><strong>Learn smarter</strong>Every day, one step</span></div><div className="orbit-card orbit-two"><span className="orbit-icon"><Trophy size={16} /></span><span><strong>Keep going</strong>Your streak is growing</span></div></div></div></div></section>
    <section className="feature-section"><div className="container"><div className="section-head"><div><span className="eyebrow">Everything in one place</span><h2 className="section-title" style={{ marginTop: 7 }}>Your learning, with momentum.</h2></div><p className="section-copy" style={{ maxWidth: 360 }}>A focused space for discovering what matters, building confidence, and making visible progress.</p></div><div className="feature-grid">{features.map((feature) => <div className="feature-card" key={feature.title}><div className={`feature-icon ${feature.tone}`}>{feature.icon}</div><h3>{feature.title}</h3><p>{feature.copy}</p></div>)}</div></div></section>
    <section className="page" style={{ paddingTop: 30 }}><div className="container"><div className="section-head"><div><span className="eyebrow">Start somewhere useful</span><h2 className="section-title" style={{ marginTop: 7 }}>Courses worth your time.</h2></div><Link to="/courses" className="btn btn-ghost">Browse all <ArrowRight size={15} /></Link></div>{state === 'loading' ? <div className="spinner" /> : state === 'error' ? <div className="error-state"><h3>Courses are taking a breather</h3><p>We could not load the catalogue right now.</p></div> : courses.length ? <div className="course-grid">{courses.map((course) => <CourseCard course={course} key={course.id} />)}</div> : <div className="empty-state"><h3>Your next course is on its way</h3><p>No published courses are available yet.</p></div>}<div className="cta-band"><div><span className="eyebrow" style={{ color: '#91b5ff' }}>Make learning feel lighter</span><h2>Small steps compound into big skills.</h2><p>Find a course, make a little progress, and let LearnVerse keep the thread for you.</p></div><Link to="/signup" className="btn btn-primary">Join LearnVerse <ArrowRight size={16} /></Link></div></div></section>
  </>;
};
export default Home;
