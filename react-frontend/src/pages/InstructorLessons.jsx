import { useEffect, useState } from 'react';
import { ArrowLeft, Plus, Trash2, Edit2, Save } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { instructorService } from '../services/instructor';

const InstructorLessons = () => {
  const { courseId } = useParams();
  const [modules, setModules] = useState([]);
  const [selectedModuleId, setSelectedModuleId] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingLesson, setEditingLesson] = useState(null);
  const [lessonForm, setLessonForm] = useState({ title: '', description: '', video_url: '', content: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      const { data } = await instructorService.getCourseModules(courseId);
      setModules(data || []);
    } catch {
      setError('Unable to load modules');
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [courseId]);

  const selectModule = (moduleId) => {
    setSelectedModuleId(moduleId);
    setShowCreateForm(false);
    setEditingLesson(null);
  };

  const createLesson = async (e) => {
    e.preventDefault();
    if (!lessonForm.title.trim()) return;
    setSaving(true);
    try {
      const { data } = await instructorService.addLesson(selectedModuleId, lessonForm);
      setModules((prev) => prev.map((m) => m.id === selectedModuleId ? { ...m, lessons: [...(m.lessons || []), data.lesson] } : m));
      setLessonForm({ title: '', description: '', video_url: '', content: '' });
      setShowCreateForm(false);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to add lesson');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (lesson) => {
    setEditingLesson(lesson);
    setLessonForm({ title: lesson.title, description: lesson.description || '', video_url: lesson.video_url || '', content: lesson.content || '' });
  };

  const saveEdit = async () => {
    if (!editingLesson || !lessonForm.title.trim()) return;
    setSaving(true);
    try {
      await instructorService.updateLesson(editingLesson.id, lessonForm);
      setModules((prev) => prev.map((m) => ({
        ...m,
        lessons: m.lessons?.map((l) => l.id === editingLesson.id ? { ...l, ...lessonForm } : l),
      })));
      setEditingLesson(null);
      setLessonForm({ title: '', description: '', video_url: '', content: '' });
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to update lesson');
    } finally {
      setSaving(false);
    }
  };

  const deleteLesson = async (lessonId) => {
    if (!window.confirm('Delete this lesson?')) return;
    try {
      await instructorService.deleteLesson(lessonId);
      setModules((prev) => prev.map((m) => ({
        ...m,
        lessons: m.lessons?.filter((l) => l.id !== lessonId),
      })));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to delete lesson');
    }
  };

  const selectedModule = modules.find((m) => m.id === selectedModuleId);

  if (loading) return <main className="page"><div className="spinner" /></main>;

  return (
    <main className="page">
      <div className="container" style={{ maxWidth: 900 }}>
        <Link to="/instructor/dashboard" className="nav-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <ArrowLeft size={15} /> Back to dashboard
        </Link>
        <div className="dashboard-header" style={{ marginTop: 22 }}>
          <div>
            <span className="eyebrow">Lesson management</span>
            <h1>Manage lessons</h1>
            <p>Create, edit, and delete lessons within your course modules.</p>
          </div>
        </div>
        {error && <div className="form-message" style={{ marginTop: 15 }}>{error}</div>}

        <section className="panel" style={{ marginTop: 22 }}>
          <div className="panel-head"><h2>Modules & Lessons</h2></div>
          {modules.length === 0 ? (
            <div className="empty-state" style={{ padding: '42px 0' }}>
              <h3 style={{ marginTop: 12 }}>No modules yet</h3>
              <p>Add a module first to start creating lessons.</p>
              <Link to={`/instructor/course/${courseId}/modules`} className="btn btn-primary" style={{ marginTop: 18 }}>Add a module</Link>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 22 }}>
                {modules.map((m, idx) => (
                  <button
                    key={m.id}
                    className={`btn ${m.id === selectedModuleId ? 'btn-primary' : 'btn-soft'}`}
                    onClick={() => selectModule(m.id)}
                  >
                    Module {idx + 1}: {m.title}
                  </button>
                ))}
              </div>

              {selectedModule && (
                <div style={{ borderTop: '1px solid var(--line)', paddingTop: 22 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                    <h2 style={{ fontSize: '1.2rem' }}>{selectedModule.title}</h2>
                    <button className="btn btn-primary" onClick={() => { setShowCreateForm(true); setEditingLesson(null); }}>
                      <Plus size={14} /> Add lesson
                    </button>
                  </div>

                  {showCreateForm && (
                    <form onSubmit={createLesson} style={{ marginBottom: 22, padding: 16, background: '#f7f9fd', borderRadius: 12 }}>
                      <div style={{ display: 'grid', gap: 12 }}>
                        <div>
                          <label className="field-label">Lesson title</label>
                          <input className="input" value={lessonForm.title} onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })} placeholder="Lesson title" required />
                        </div>
                        <div>
                          <label className="field-label">Description</label>
                          <textarea className="textarea" value={lessonForm.description} onChange={(e) => setLessonForm({ ...lessonForm, description: e.target.value })} placeholder="Brief description" />
                        </div>
                        <div>
                          <label className="field-label">Video URL</label>
                          <input className="input" value={lessonForm.video_url} onChange={(e) => setLessonForm({ ...lessonForm, video_url: e.target.value })} placeholder="https://..." />
                        </div>
                        <div>
                          <label className="field-label">Content</label>
                          <textarea className="textarea" value={lessonForm.content} onChange={(e) => setLessonForm({ ...lessonForm, content: e.target.value })} placeholder="Written content for this lesson" />
                        </div>
                        <div style={{ display: 'flex', gap: 10 }}>
                          <button type="submit" className="btn btn-primary" disabled={saving}>
                            {saving ? 'Saving...' : 'Add lesson'}
                          </button>
                          <button type="button" className="btn btn-ghost" onClick={() => { setShowCreateForm(false); setLessonForm({ title: '', description: '', video_url: '', content: '' }); }}>Cancel</button>
                        </div>
                      </div>
                    </form>
                  )}

                  {editingLesson && (
                    <form onSubmit={(e) => { e.preventDefault(); saveEdit(); }} style={{ marginBottom: 22, padding: 16, background: '#f7f9fd', borderRadius: 12 }}>
                      <div style={{ display: 'grid', gap: 12 }}>
                        <div>
                          <label className="field-label">Lesson title</label>
                          <input className="input" value={lessonForm.title} onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })} required />
                        </div>
                        <div>
                          <label className="field-label">Description</label>
                          <textarea className="textarea" value={lessonForm.description} onChange={(e) => setLessonForm({ ...lessonForm, description: e.target.value })} />
                        </div>
                        <div>
                          <label className="field-label">Video URL</label>
                          <input className="input" value={lessonForm.video_url} onChange={(e) => setLessonForm({ ...lessonForm, video_url: e.target.value })} />
                        </div>
                        <div>
                          <label className="field-label">Content</label>
                          <textarea className="textarea" value={lessonForm.content} onChange={(e) => setLessonForm({ ...lessonForm, content: e.target.value })} />
                        </div>
                        <div style={{ display: 'flex', gap: 10 }}>
                          <button type="submit" className="btn btn-primary" disabled={saving}>
                            <Save size={14} /> {saving ? 'Saving...' : 'Save changes'}
                          </button>
                          <button type="button" className="btn btn-ghost" onClick={() => { setEditingLesson(null); setLessonForm({ title: '', description: '', video_url: '', content: '' }); }}>Cancel</button>
                        </div>
                      </div>
                    </form>
                  )}

                  {selectedModule.lessons?.length === 0 && !showCreateForm && !editingLesson && (
                    <div className="empty-state">
                      <h3>No lessons yet</h3>
                      <p>Add the first lesson to this module above.</p>
                    </div>
                  )}

                  {selectedModule.lessons?.length > 0 && (
                    <div style={{ display: 'grid', gap: 10 }}>
                      {selectedModule.lessons.map((lesson) => (
                        <div key={lesson.id} className="learning-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px' }}>
                          <div>
                            <h3 style={{ fontSize: '1rem', marginBottom: 2 }}>{lesson.title}</h3>
                            <p className="muted" style={{ fontSize: '.82rem' }}>{lesson.description || 'No description'}</p>
                          </div>
                          <div style={{ display: 'flex', gap: 6 }}>
                            <button className="btn btn-soft" onClick={() => startEdit(lesson)} aria-label={`Edit ${lesson.title}`}>
                              <Edit2 size={14} />
                            </button>
                            <button className="btn btn-soft" onClick={() => deleteLesson(lesson.id)} aria-label={`Delete ${lesson.title}`} style={{ color: '#dc2626' }}>
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
};

export default InstructorLessons;
