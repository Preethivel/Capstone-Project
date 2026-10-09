import { useEffect, useState } from 'react';
import { RotateCcw, Search, SlidersHorizontal } from 'lucide-react';
import CourseCard from '../components/CourseCard';
import { getCourses, searchCourses } from '../services/courses';

const Courses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({ domain: 'all', level: 'all', price: 'all' });
  const load = async (search = false) => { setLoading(true); setError(''); const result = search ? await searchCourses(query, filters.domain, filters.level, filters.price) : await getCourses(); if (result.success) setCourses(result.data || []); else setError(result.message || 'Could not load courses'); setLoading(false); };
  // The initial request intentionally runs once; filter actions call load explicitly.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, []);
  const reset = () => { setQuery(''); setFilters({ domain: 'all', level: 'all', price: 'all' }); setTimeout(() => load(), 0); };
  return <main className="page"><div className="container"><span className="eyebrow">The catalogue</span><h1 className="page-title" style={{ marginTop: 10 }}>Find your next <span style={{ color: 'var(--blue)' }}>breakthrough.</span></h1><p className="section-copy" style={{ maxWidth: 620, marginTop: 14 }}>Explore practical courses from instructors who care about helping you make real progress.</p><div className="toolbar"><div className="search-field"><Search size={18} /><input className="input" value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && load(true)} placeholder="Search by course title or topic" aria-label="Search courses" /></div><div className="filter-row"><select className="select" value={filters.domain} onChange={(event) => setFilters({ ...filters, domain: event.target.value })} aria-label="Filter by domain"><option value="all">All topics</option><option>Programming</option><option>Web Development</option><option>AI & ML</option><option>Data Science</option><option>Cybersecurity</option><option>Cloud Computing</option><option>DevOps</option></select><select className="select" value={filters.level} onChange={(event) => setFilters({ ...filters, level: event.target.value })} aria-label="Filter by level"><option value="all">All levels</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select><button className="btn btn-primary" onClick={() => load(true)}><SlidersHorizontal size={16} /> Filter</button><button className="btn btn-ghost" onClick={reset} aria-label="Reset filters"><RotateCcw size={16} /></button></div></div>{loading ? <div className="spinner" /> : error ? <div className="error-state"><h3>We could not load the catalogue</h3><p>{error}</p><button className="btn btn-primary" style={{ marginTop: 18 }} onClick={() => load()}>Try again</button></div> : courses.length ? <div className="course-grid">{courses.map((course) => <CourseCard course={course} key={course.id} />)}</div> : <div className="empty-state"><div className="empty-state-icon"><Search size={23} /></div><h3>No courses match that search</h3><p>Try a broader topic or clear the filters.</p><button className="btn btn-soft" style={{ marginTop: 18 }} onClick={reset}>Clear filters</button></div>}</div></main>;
};
export default Courses;
