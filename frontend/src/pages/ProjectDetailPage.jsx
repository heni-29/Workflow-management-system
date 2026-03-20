// src/pages/ProjectDetailPage.jsx
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Plus, ArrowLeft, X } from 'lucide-react';
import { projectsApi, tasksApi, usersApi } from '../api/client';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { formatDate } from '../utils/time';

const STATUS_OPTIONS = [
    { value: 'todo', label: 'To Do' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'review', label: 'In Review' },
    { value: 'done', label: 'Done' },
];

function CreateTaskModal({ projectId, users, onClose, onCreated }) {
    const [form, setForm] = useState({
        title: '', description: '', status: 'todo', priority: 2,
        assignee_id: '', due_date: '',
    });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        const payload = { ...form, project: projectId };
        if (!payload.assignee_id) delete payload.assignee_id;
        if (!payload.due_date) delete payload.due_date;
        try {
            const { data } = await tasksApi.create(payload);
            onCreated(data);
            onClose();
        } catch (err) {
            setError(err.response?.data?.title?.[0] ?? 'Something went wrong.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <span className="modal-title">New Task</span>
                    <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
                </div>
                {error && <div className="login-error">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Title</label>
                        <input
                            type="text"
                            value={form.title}
                            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                            placeholder="Task title"
                            required autoFocus
                        />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            rows={2}
                            value={form.description}
                            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                            placeholder="Optional description"
                        />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                        <div className="form-group">
                            <label>Status</label>
                            <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                                {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Priority</label>
                            <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: Number(e.target.value) }))}>
                                <option value={1}>Low</option>
                                <option value={2}>Medium</option>
                                <option value={3}>High</option>
                            </select>
                        </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                        <div className="form-group">
                            <label>Assignee</label>
                            <select value={form.assignee_id} onChange={e => setForm(f => ({ ...f, assignee_id: e.target.value }))}>
                                <option value="">Unassigned</option>
                                {users.map(u => <option key={u.id} value={u.id}>{u.username}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Due Date</label>
                            <input
                                type="date"
                                value={form.due_date}
                                onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
                            />
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
                        <button type="submit" className="btn btn-primary" disabled={saving}>
                            {saving ? 'Creating…' : 'Create Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default function ProjectDetailPage() {
    const { id } = useParams();
    const [project, setProject] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        Promise.all([
            projectsApi.get(id),
            projectsApi.tasks(id),
            projectsApi.stats(id),
            usersApi.list({ page_size: 100 }),
        ]).then(([pRes, tRes, sRes, uRes]) => {
            setProject(pRes.data);
            setTasks(tRes.data.results ?? tRes.data);
            setStats(sRes.data);
            setUsers(uRes.data.results ?? uRes.data);
        }).finally(() => setLoading(false));
    }, [id]);

    if (loading) return <div className="spinner" style={{ marginTop: '4rem' }} />;
    if (!project) return <p style={{ padding: '2rem', color: 'var(--danger)' }}>Project not found.</p>;

    const chartData = stats
        ? Object.entries(stats.by_status).map(([key, val]) => ({
            name: val.label, count: val.count,
        }))
        : [];

    const barColors = ['#6366f1', '#38bdf8', '#f59e0b', '#22c55e'];

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <Link to="/projects" style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 8 }}>
                        <ArrowLeft size={14} /> Projects
                    </Link>
                    <h1 className="page-title">{project.name}</h1>
                    {project.description && (
                        <p className="page-subtitle">{project.description}</p>
                    )}
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    <Plus size={16} /> Add Task
                </button>
            </div>

            {/* Stats + chart */}
            <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div className="card">
                    <div className="card-header"><span className="card-title">Task Breakdown</span></div>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="name" tick={{ fill: '#8b949e', fontSize: 12 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#8b949e', fontSize: 12 }} axisLine={false} tickLine={false} />
                            <Tooltip
                                contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, color: '#f0f6fc' }}
                                cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                            />
                            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                {chartData.map((_, i) => (
                                    <Bar key={i} dataKey="count" fill={barColors[i % barColors.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="card">
                    <div className="card-header"><span className="card-title">Project Info</span></div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                        <Row label="Total Tasks" value={stats?.total_tasks ?? 0} />
                        <Row label="Overdue" value={stats?.overdue ?? 0} color="var(--danger)" />
                        <Row label="Members" value={project.members?.length ?? 0} />
                        <Row label="Created by" value={project.created_by?.username ?? '—'} />
                    </div>
                    <div style={{ marginTop: '1rem' }}>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 6 }}>Members</div>
                        <div className="avatar-stack">
                            {(project.members ?? []).slice(0, 8).map(m => (
                                <div key={m.id} className="avatar-sm" title={m.username}>
                                    {(m.first_name?.[0] ?? m.username?.[0] ?? '?').toUpperCase()}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Task table */}
            <div className="card" style={{ padding: 0 }}>
                <div className="card-header" style={{ padding: '1.25rem 1.5rem' }}>
                    <span className="card-title">Tasks ({tasks.length})</span>
                </div>
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Status</th>
                                <th>Priority</th>
                                <th>Assignee</th>
                                <th>Due Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tasks.length === 0 ? (
                                <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem' }}>
                                    No tasks yet. Add one!
                                </td></tr>
                            ) : tasks.map(t => (
                                <tr key={t.id}>
                                    <td>
                                        <div style={{ fontWeight: 500 }}>{t.title}</div>
                                        {t.is_overdue && <span className="overdue-tag">Overdue</span>}
                                    </td>
                                    <td><StatusBadge status={t.status} /></td>
                                    <td><PriorityBadge priority={t.priority} /></td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        {t.assignee?.username ?? <span style={{ color: 'var(--text-muted)' }}>Unassigned</span>}
                                    </td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                        {t.due_date ? formatDate(t.due_date) : '—'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {showModal && (
                <CreateTaskModal
                    projectId={Number(id)}
                    users={users}
                    onClose={() => setShowModal(false)}
                    onCreated={(t) => setTasks(prev => [t, ...prev])}
                />
            )}
        </div>
    );
}

function Row({ label, value, color }) {
    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
            <span style={{ fontWeight: 600, color: color ?? 'var(--text-primary)' }}>{value}</span>
        </div>
    );
}
