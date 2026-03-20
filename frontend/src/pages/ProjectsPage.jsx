// src/pages/ProjectsPage.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, FolderKanban, Users, CheckSquare, X } from 'lucide-react';
import { projectsApi, usersApi } from '../api/client';
import { useAuth } from '../context/AuthContext';

function CreateProjectModal({ onClose, onCreated }) {
    const [form, setForm] = useState({ name: '', description: '' });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            const { data } = await projectsApi.create(form);
            onCreated(data);
            onClose();
        } catch (err) {
            setError(err.response?.data?.name?.[0] ?? 'Something went wrong.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <span className="modal-title">New Project</span>
                    <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
                </div>
                {error && <div className="login-error">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Project Name</label>
                        <input
                            type="text"
                            placeholder="e.g. CS Capstone"
                            value={form.name}
                            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                            required
                            autoFocus
                        />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            rows={3}
                            placeholder="What is this project about?"
                            value={form.description}
                            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                        />
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={saving}>
                            {saving ? 'Creating…' : 'Create Project'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function ProjectsPage() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const { user } = useAuth();

    const load = () => {
        setLoading(true);
        projectsApi.list({ page_size: 100 })
            .then(r => setProjects(r.data.results ?? r.data))
            .finally(() => setLoading(false));
    };

    useEffect(load, []);

    const handleCreated = (proj) => setProjects(prev => [proj, ...prev]);

    if (loading) return <div className="spinner" style={{ marginTop: '4rem' }} />;

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Projects</h1>
                    <p className="page-subtitle">{projects.length} projects total</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    <Plus size={16} /> New Project
                </button>
            </div>

            {projects.length === 0 ? (
                <div className="empty-state">
                    <FolderKanban />
                    <h3>No projects yet</h3>
                    <p>Create your first project to get started.</p>
                </div>
            ) : (
                <div className="project-cards">
                    {projects.map(p => {
                        const pct = p.task_count
                            ? Math.round(((p.task_count - p.open_task_count) / p.task_count) * 100)
                            : 0;

                        return (
                            <Link to={`/projects/${p.id}`} key={p.id} style={{ textDecoration: 'none' }}>
                                <div className="project-card">
                                    <div className="project-card-header">
                                        <div>
                                            <div className="project-name">{p.name}</div>
                                        </div>
                                        <div style={{
                                            display: 'flex', alignItems: 'center', gap: 4,
                                            fontSize: '0.78rem', color: 'var(--accent-hover)', fontWeight: 600,
                                        }}>
                                            {pct}%
                                        </div>
                                    </div>

                                    {p.description && (
                                        <p className="project-desc" style={{
                                            display: '-webkit-box', WebkitLineClamp: 2,
                                            WebkitBoxOrient: 'vertical', overflow: 'hidden',
                                        }}>
                                            {p.description}
                                        </p>
                                    )}

                                    <div className="project-progress-bar-wrap">
                                        <div className="project-progress-bar" style={{ width: `${pct}%` }} />
                                    </div>

                                    <div className="project-meta">
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                                            <CheckSquare size={13} />
                                            {p.open_task_count} open / {p.task_count} total
                                        </span>
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                                            <Users size={13} />
                                            {p.members?.length ?? 0} members
                                        </span>
                                    </div>
                                </div>
                            </Link>
                        );
                    })}
                </div>
            )}

            {showModal && (
                <CreateProjectModal onClose={() => setShowModal(false)} onCreated={handleCreated} />
            )}
        </div>
    );
}
