// src/pages/ActivityPage.jsx
import { useEffect, useState } from 'react';
import { activitiesApi } from '../api/client';
import { formatRelative } from '../utils/time';
import { Activity } from 'lucide-react';

const DOT_COLORS = {
    create: '#22c55e',
    update: '#6366f1',
    delete: '#ef4444',
    status_change: '#38bdf8',
};

export default function ActivityPage() {
    const [activities, setActivities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(false);

    const load = (p = 1) => {
        setLoading(true);
        activitiesApi.list({ page: p, page_size: 20 })
            .then(r => {
                const results = r.data.results ?? r.data;
                setActivities(prev => p === 1 ? results : [...prev, ...results]);
                setHasMore(!!r.data.next);
                setPage(p);
            })
            .finally(() => setLoading(false));
    };

    useEffect(() => { load(1); }, []);

    const dotColor = (verb = '') => {
        const v = verb.toLowerCase();
        if (v.includes('creat')) return DOT_COLORS.create;
        if (v.includes('delet')) return DOT_COLORS.delete;
        if (v.includes('status')) return DOT_COLORS.status_change;
        return DOT_COLORS.update;
    };

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Activity Log</h1>
                    <p className="page-subtitle">All recent changes across the workspace</p>
                </div>
            </div>

            <div className="card">
                {activities.length === 0 && !loading ? (
                    <div className="empty-state">
                        <Activity />
                        <h3>No activity yet</h3>
                        <p>Actions on projects and tasks will appear here.</p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                        {activities.map((a, i) => (
                            <div
                                key={a.id}
                                className="activity-item"
                                style={{
                                    paddingBottom: '1.1rem',
                                    marginBottom: '1.1rem',
                                    borderBottom:
                                        i < activities.length - 1
                                            ? '1px solid var(--border)'
                                            : 'none',
                                }}
                            >
                                {/* Avatar */}
                                <div
                                    style={{
                                        width: 34, height: 34, borderRadius: '50%',
                                        background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '0.75rem', fontWeight: 700, color: '#fff', flexShrink: 0,
                                    }}
                                >
                                    {(a.user?.first_name?.[0] ?? a.user?.username?.[0] ?? '?').toUpperCase()}
                                </div>

                                <div style={{ flex: 1 }}>
                                    <div className="activity-text">
                                        <span>{a.user?.username}</span>{' '}
                                        <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{a.verb}</span>
                                        {a.detail && (
                                            <span style={{ color: 'var(--text-secondary)' }}>
                                                {' '}&mdash;{' '}{typeof a.detail === 'string' ? a.detail : JSON.stringify(a.detail)}
                                            </span>
                                        )}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                                        <div
                                            style={{
                                                width: 7, height: 7, borderRadius: '50%',
                                                background: dotColor(a.verb), flexShrink: 0,
                                            }}
                                        />
                                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                            {a.target_type && (
                                                <span
                                                    style={{
                                                        background: 'var(--bg-tertiary)',
                                                        padding: '1px 6px', borderRadius: 4,
                                                        fontSize: '0.68rem', marginRight: 6,
                                                    }}
                                                >
                                                    {a.target_type}
                                                </span>
                                            )}
                                            {formatRelative(a.timestamp)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {loading && <div className="spinner" style={{ marginTop: '2rem' }} />}

                {hasMore && !loading && (
                    <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                        <button
                            className="btn btn-secondary"
                            onClick={() => load(page + 1)}
                        >
                            Load more
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
