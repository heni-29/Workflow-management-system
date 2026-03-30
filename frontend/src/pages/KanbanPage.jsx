// src/pages/KanbanPage.jsx
import { useEffect, useState } from 'react';
import { tasksApi, projectsApi } from '../api/client';
import { GripVertical, Plus, X, Filter } from 'lucide-react';
import { PriorityBadge } from '../components/Badges';
import { formatDate } from '../utils/time';

const COLUMNS = [
    { key: 'todo', label: 'To Do', color: 'gray' },
    { key: 'in_progress', label: 'In Progress', color: 'blue' },
    { key: 'review', label: 'In Review', color: 'yellow' },
    { key: 'done', label: 'Done', color: 'green' },
];

const COLORS = {
    gray: { bg: 'rgba(107, 114, 128, 0.1)', border: 'rgba(107, 114, 128, 0.3)', text: '#9ca3af' },
    blue: { bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.3)', text: '#60a5fa' },
    yellow: { bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.3)', text: '#fbbf24' },
    green: { bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.3)', text: '#4ade80' },
};

function TaskCard({ task, onDragStart }) {
    const isOverdue = task.is_overdue;
    
    return (
        <div
            className="kanban-card"
            draggable
            onDragStart={(e) => onDragStart(e, task)}
            style={{
                cursor: 'grab',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                padding: '0.875rem',
                marginBottom: '0.75rem',
                transition: 'var(--transition)',
            }}
            onMouseDown={(e) => e.currentTarget.style.cursor = 'grabbing'}
            onMouseUp={(e) => e.currentTarget.style.cursor = 'grab'}
        >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <GripVertical size={14} color="var(--text-muted)" style={{ marginTop: '0.125rem', flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        color: 'var(--text-primary)',
                        marginBottom: '0.375rem',
                        lineHeight: 1.4,
                    }}>
                        {task.title}
                    </div>
                    {task.description && (
                        <div style={{
                            fontSize: '0.75rem',
                            color: 'var(--text-secondary)',
                            lineHeight: 1.5,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                        }}>
                            {task.description}
                        </div>
                    )}
                </div>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <PriorityBadge priority={task.priority} />
                    {task.due_date && (
                        <span style={{
                            fontSize: '0.7rem',
                            color: isOverdue ? 'var(--danger)' : 'var(--text-muted)',
                            fontWeight: isOverdue ? 600 : 400,
                        }}>
                            {formatDate(task.due_date)}
                        </span>
                    )}
                </div>
                {task.assignee && (
                    <div style={{
                        fontSize: '0.7rem',
                        color: 'var(--text-secondary)',
                        background: 'var(--bg-tertiary)',
                        padding: '0.125rem 0.5rem',
                        borderRadius: 'var(--radius-sm)',
                    }}>
                        {task.assignee.username}
                    </div>
                )}
            </div>
        </div>
    );
}

function KanbanColumn({ column, tasks, onDrop, onDragOver }) {
    const color = COLORS[column.color];
    
    return (
        <div
            className="kanban-column"
            onDrop={onDrop}
            onDragOver={onDragOver}
            style={{
                flex: '1 1 0',
                minWidth: '280px',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                maxHeight: 'calc(100vh - 180px)',
            }}
            data-status={column.key}
        >
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '1rem',
                paddingBottom: '0.75rem',
                borderBottom: `2px solid ${color.border}`,
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: color.text,
                    }} />
                    <h3 style={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: color.text,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                    }}>
                        {column.label}
                    </h3>
                </div>
                <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: 'var(--text-muted)',
                    background: color.bg,
                    padding: '0.125rem 0.5rem',
                    borderRadius: 'var(--radius-sm)',
                }}>
                    {tasks.length}
                </span>
            </div>

            <div style={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'hidden',
                paddingRight: '0.25rem',
            }}>
                {tasks.length === 0 ? (
                    <div style={{
                        textAlign: 'center',
                        color: 'var(--text-muted)',
                        fontSize: '0.8rem',
                        padding: '2rem 1rem',
                    }}>
                        Drop tasks here
                    </div>
                ) : (
                    tasks.map(task => (
                        <TaskCard key={task.id} task={task} onDragStart={(e, t) => {
                            e.dataTransfer.effectAllowed = 'move';
                            e.dataTransfer.setData('taskId', t.id);
                            e.dataTransfer.setData('fromStatus', t.status);
                        }} />
                    ))
                )}
            </div>
        </div>
    );
}

export default function KanbanPage() {
    const [tasks, setTasks] = useState([]);
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProjects();
        loadTasks();
    }, [selectedProject]);

    const loadProjects = async () => {
        try {
            const { data } = await projectsApi.list();
            setProjects(data.results || data);
        } catch (err) {
            console.error('Failed to load projects:', err);
        }
    };

    const loadTasks = async () => {
        setLoading(true);
        try {
            const params = {};
            if (selectedProject) {
                params.project = selectedProject;
            }
            const { data } = await tasksApi.list(params);
            setTasks(data.results || data);
        } catch (err) {
            console.error('Failed to load tasks:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData('taskId');
        const fromStatus = e.dataTransfer.getData('fromStatus');
        
        const columnEl = e.currentTarget;
        const toStatus = columnEl.dataset.status;
        
        if (fromStatus === toStatus) return;

        try {
            await tasksApi.setStatus(taskId, toStatus);
            
            setTasks(prev => prev.map(task =>
                task.id === parseInt(taskId)
                    ? { ...task, status: toStatus }
                    : task
            ));
        } catch (err) {
            console.error('Failed to update task status:', err);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    const tasksByStatus = COLUMNS.reduce((acc, col) => {
        acc[col.key] = tasks.filter(t => t.status === col.key);
        return acc;
    }, {});

    return (
        <div className="page">
            <div style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div>
                        <h1 className="page-title">Kanban Board</h1>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                            Drag and drop tasks to update their status
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Filter size={16} color="var(--text-secondary)" />
                            <select
                                value={selectedProject}
                                onChange={(e) => setSelectedProject(e.target.value)}
                                style={{
                                    background: 'var(--bg-secondary)',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-primary)',
                                    padding: '0.5rem 0.75rem',
                                    borderRadius: 'var(--radius-sm)',
                                    fontSize: '0.875rem',
                                    minWidth: '200px',
                                }}
                            >
                                <option value="">All Projects</option>
                                {projects.map(p => (
                                    <option key={p.id} value={p.id}>{p.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                    Loading tasks...
                </div>
            ) : (
                <div style={{
                    display: 'flex',
                    gap: '1rem',
                    overflowX: 'auto',
                    paddingBottom: '1rem',
                }}>
                    {COLUMNS.map(column => (
                        <KanbanColumn
                            key={column.key}
                            column={column}
                            tasks={tasksByStatus[column.key] || []}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
