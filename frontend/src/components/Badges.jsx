// src/components/Badges.jsx

const STATUS_MAP = {
    todo: { label: 'To Do', cls: 'badge-todo' },
    in_progress: { label: 'In Progress', cls: 'badge-progress' },
    review: { label: 'In Review', cls: 'badge-review' },
    done: { label: 'Done', cls: 'badge-done' },
};

const PRIORITY_MAP = {
    1: { label: 'Low', cls: 'badge-low' },
    2: { label: 'Medium', cls: 'badge-medium' },
    3: { label: 'High', cls: 'badge-high' },
};

export function StatusBadge({ status }) {
    const { label, cls } = STATUS_MAP[status] ?? { label: status, cls: '' };
    return <span className={`badge ${cls}`}>{label}</span>;
}

export function PriorityBadge({ priority }) {
    const { label, cls } = PRIORITY_MAP[priority] ?? { label: priority, cls: '' };
    return <span className={`badge ${cls}`}>{label}</span>;
}
