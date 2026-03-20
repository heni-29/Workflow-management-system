// src/pages/TasksPage.jsx
import { useEffect, useState } from 'react';
import { Plus, X, Filter } from 'lucide-react';
import { tasksApi, projectsApi, usersApi } from '../api/client';
import { StatusBadge, PriorityBadge } from '../components/Badges';
import { formatDate } from '../utils/time';

const STATUS_OPTIONS = [
    { value: '', label: 'All Statuses' },
    { value: 'todo', label: 'To Do' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'review', label: 'In Review' },
    { value: 'done', label: 'Done' },
];

function EditStatusModal({ task, onClose, onUpdated }) {
    const [status, setStatus] = useState(task.status);
    const [saving, setSaving] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        const { data } = await tasksApi.setStatus(task.id, status);
        onUpdated(data);
        onClose();
        setSaving(false);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ width: 340 }} onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <span className="modal-title">Update Status</span>
                    <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
                </div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    {task.title}
                </p>
                <div className="form-group">
                    <label>Status</label>
                    <select value={status} onChange={e => setStatus(e.target.value)}>
                        {STATUS_OPTIONS.slice(1).map(s => (
                            <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                    </select>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                        {saving ? 'Saving…' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function TasksPage() {
    const [tasks, setTasks] = useState([]);
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);

    const [filterStatus, setFilterStatus] = useState('');
    const [filterProject, setFilterProject] = useState('');

    const [editTask, setEditTask] = useState(null);

    const load = (params = {}) => {
        setLoading(true);
        tasksApi.list({ page_size: 100, ...params })
            .then(r => setTasks(r.data.results ?? r.data))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        projectsApi.list({ page_size: 100 }).then(r =>
            setProjects(r.data.results ?? r.data)
        );
        load();
    }, []);

    const applyFilters = (status, project) => {
        const params = {};
        if (status) params.status = status;
        if (project) params.project = project;
        load(params);
    };

    const handleStatusChange = (val) => {
        setFilterStatus(val);
        applyFilters(val, filterProject);
    };

    const handleProjectChange = (val) => {
        setFilterProject(val);
        applyFilters(filterStatus, val);
    };

    const handleUpdated = (updated) =>
        setTasks(prev => prev.map(t => (t.id === updated.id ? updated : t)));

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Tasks</h1>
                    <p className="page-subtitle">{tasks.length} tasks</p>
                </div>
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    <Filter size={15} /> Filters:
                </div>
                <select
                    style={{ width: 'auto', padding: '0.4rem 0.75rem' }}
                    value={filterStatus}
                    onChange={e => handleStatusChange(e.target.value)}
                >
                    {STATUS_OPTIONS.map(s => (
                        <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                </select>
                <select
                    style={{ width: 'auto', padding: '0.4rem 0.75rem' }}
                    value={filterProject}
                    onChange={e => handleProjectChange(e.target.value)}
                >
                    <option value="">All Projects</option>
                    {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
            </div>

            <div className="card" style={{ padding: 0 }}>
                <div className="table-wrap">
                    {loading ? (
                        <div className="spinner" style={{ marginTop: '4rem' }} />
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Project</th>
                                    <th>Status</th>
                                    <th>Priority</th>
                                    <th>Assignee</th>
                                    <th>Due Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tasks.length === 0 ? (
                                    <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem' }}>
                                        No tasks found.
                                    </td></tr>
                                ) : tasks.map(t => (
                                    <tr
                                        key={t.id}
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => setEditTask(t)}
                                    >
                                        <td>
                                            <div style={{ fontWeight: 500 }}>{t.title}</div>
                                            {t.is_overdue && <span className="overdue-tag">Overdue</span>}
                                        </td>
                                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                            {t.project_name}
                                        </td>
                                        <td><StatusBadge status={t.status} /></td>
                                        <td><PriorityBadge priority={t.priority} /></td>
                                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                            {t.assignee?.username ?? <span style={{ color: 'var(--text-muted)' }}>—</span>}
                                        </td>
                                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                            {t.due_date ? formatDate(t.due_date) : '—'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {editTask && (
                <EditStatusModal
                    task={editTask}
                    onClose={() => setEditTask(null)}
                    onUpdated={handleUpdated}
                />
            )}
        </div>
    );
}
