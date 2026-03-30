// src/pages/DashboardPage.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
    FolderKanban, CheckSquare, Clock, AlertCircle, TrendingUp
} from 'lucide-react';
import { projectsApi, tasksApi, activitiesApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { formatRelative } from '../utils/time';

const STATUS_COLORS = {
    todo: '#6366f1',
    in_progress: '#38bdf8',
    review: '#f59e0b',
    done: '#22c55e',
};

export default function DashboardPage() {
    const { user } = useAuth();
    const [projects, setProjects] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [activities, setActivities] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            projectsApi.list({ page_size: 100 }),
            tasksApi.list({ page_size: 100 }),
            activitiesApi.list({ page_size: 10 }),
        ]).then(([pRes, tRes, aRes]) => {
            setProjects(pRes.data.results ?? pRes.data);
            setTasks(tRes.data.results ?? tRes.data);
            setActivities(aRes.data.results ?? aRes.data);
        }).finally(() => setLoading(false));
    }, []);

    if (loading) return <div className="spinner" style={{ marginTop: '4rem' }} />;

    // ── Derived stats ──────────────────────────────────────────────────────────
    const totalProjects = projects.length;
    const totalTasks = tasks.length;
    const doneTasks = tasks.filter(t => t.status === 'done').length;
    const overdueTasks = tasks.filter(t => t.is_overdue).length;

    // Bar chart: tasks by status, per project (top 5)
    const topProjects = [...projects]
        .sort((a, b) => b.task_count - a.task_count)
        .slice(0, 6);

    const barData = topProjects.map(p => ({
        name: p.name.length > 14 ? p.name.slice(0, 12) + '…' : p.name,
        total: p.task_count,
        open: p.open_task_count,
    }));

    // Pie chart: tasks by status
    const statusCounts = ['todo', 'in_progress', 'review', 'done'].map(s => ({
        name: { todo: 'To Do', in_progress: 'In Progress', review: 'Review', done: 'Done' }[s],
        value: tasks.filter(t => t.status === s).length,
        color: STATUS_COLORS[s],
    })).filter(d => d.value > 0);

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">
                        Good morning, {user?.first_name || user?.username}!
                    </h1>
                    <p className="page-subtitle">Here's what's happening across your projects.</p>
                </div>
                <Link to="/projects" className="btn btn-primary">
                    <FolderKanban size={15} /> All Projects
                </Link>
            </div>

            {/* Stat cards */}
            <div className="stat-cards">
                <div className="stat-card">
                    <div className="stat-icon accent"><FolderKanban size={22} /></div>
                    <div className="stat-body">
                        <div className="stat-value">{totalProjects}</div>
                        <div className="stat-label">Active Projects</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon info"><CheckSquare size={22} /></div>
                    <div className="stat-body">
                        <div className="stat-value">{totalTasks}</div>
                        <div className="stat-label">Total Tasks</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon success"><TrendingUp size={22} /></div>
                    <div className="stat-body">
                        <div className="stat-value">{doneTasks}</div>
                        <div className="stat-label">Completed</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon danger"><AlertCircle size={22} /></div>
                    <div className="stat-body">
                        <div className="stat-value">{overdueTasks}</div>
                        <div className="stat-label">Overdue</div>
                    </div>
                </div>
            </div>

            {/* Charts row */}
            <div className="dashboard-charts">
                {/* Bar chart */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Tasks by Project</span>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={barData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="name" tick={{ fill: '#8b949e', fontSize: 12 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#8b949e', fontSize: 12 }} axisLine={false} tickLine={false} />
                            <Tooltip
                                contentStyle={{
                                    background: '#21262d',
                                    border: '1px solid rgba(255,255,255,0.08)',
                                    borderRadius: 8,
                                    fontSize: 13,
                                    color: '#f0f6fc',
                                }}
                                cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                            />
                            <Bar dataKey="total" name="Total" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="open" name="Open" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Pie chart */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Task Status</span>
                    </div>
                    {statusCounts.length === 0 ? (
                        <div className="empty-state" style={{ padding: '3rem 1rem' }}>
                            <p>No tasks yet</p>
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height={240}>
                            <PieChart>
                                <Pie
                                    data={statusCounts}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={55}
                                    outerRadius={90}
                                    paddingAngle={3}
                                    dataKey="value"
                                >
                                    {statusCounts.map((entry, i) => (
                                        <Cell key={i} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: '#21262d',
                                        border: '1px solid rgba(255,255,255,0.08)',
                                        borderRadius: 8,
                                        fontSize: 13,
                                        color: '#f0f6fc',
                                    }}
                                />
                                <Legend
                                    iconType="circle"
                                    iconSize={8}
                                    formatter={(v) => <span style={{ color: '#8b949e', fontSize: 12 }}>{v}</span>}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    )}
                </div>
            </div>

            {/* Bottom row: recent projects + activity */}
            <div className="grid-2" style={{ gap: '1.5rem' }}>
                {/* Recent projects */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Recent Projects</span>
                        <Link to="/projects" className="btn btn-ghost btn-sm">View all →</Link>
                    </div>
                    <div className="task-list">
                        {projects.slice(0, 5).map(p => {
                            const pct = p.task_count
                                ? Math.round(((p.task_count - p.open_task_count) / p.task_count) * 100)
                                : 0;
                            return (
                                <Link to={`/projects/${p.id}`} key={p.id} style={{ textDecoration: 'none' }}>
                                    <div className="task-item">
                                        <div style={{ flex: 1 }}>
                                            <div className="task-title">{p.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                                                {p.task_count} tasks · {p.open_task_count} open
                                            </div>
                                            <div className="project-progress-bar-wrap" style={{ marginTop: 8 }}>
                                                <div className="project-progress-bar" style={{ width: `${pct}%` }} />
                                            </div>
                                        </div>
                                        <span style={{ fontSize: '0.78rem', color: 'var(--accent-hover)', fontWeight: 600 }}>
                                            {pct}%
                                        </span>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>

                {/* Activity feed */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Recent Activity</span>
                        <Link to="/activity" className="btn btn-ghost btn-sm">View all →</Link>
                    </div>
                    {activities.length === 0 ? (
                        <p className="text-muted">No activity yet.</p>
                    ) : (
                        <div className="activity-list">
                            {activities.slice(0, 8).map(a => (
                                <div key={a.id} className="activity-item">
                                    <div className="activity-dot" />
                                    <div>
                                        <div className="activity-text">
                                            <span>{a.user?.username}</span> {a.verb}{' '}
                                            {a.detail ? `— ${typeof a.detail === 'string' ? a.detail : JSON.stringify(a.detail)}` : ''}
                                        </div>
                                        <div className="activity-time">{formatRelative(a.timestamp)}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
