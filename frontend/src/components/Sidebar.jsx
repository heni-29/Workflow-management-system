// src/components/Sidebar.jsx
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard, FolderKanban, CheckSquare, Activity,
    LogOut, Workflow, KanbanSquare
} from 'lucide-react';

const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/projects', label: 'Projects', icon: FolderKanban },
    { to: '/tasks', label: 'Tasks', icon: CheckSquare },
    { to: '/kanban', label: 'Kanban', icon: KanbanSquare },
    { to: '/activity', label: 'Activity', icon: Activity },
];

export default function Sidebar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const initials = user
        ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? user.username?.[0] ?? '?'}`.toUpperCase()
        : '?';

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">W</div>
                <span className="sidebar-logo-text">Workflow</span>
            </div>

            <div className="sidebar-section-label">Navigation</div>

            <nav className="sidebar-nav">
                {links.map(({ to, label, icon: Icon }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        className={({ isActive }) =>
                            `sidebar-link${isActive ? ' active' : ''}`
                        }
                    >
                        <Icon size={17} />
                        {label}
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-user">
                    <div className="sidebar-avatar">{initials}</div>
                    <div className="sidebar-user-info">
                        <div className="sidebar-username">
                            {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.username}
                        </div>
                        <div className="sidebar-role">{user?.role ?? 'Member'}</div>
                    </div>
                    <button className="sidebar-logout-btn" onClick={handleLogout} title="Sign out">
                        <LogOut size={15} />
                    </button>
                </div>
            </div>
        </aside>
    );
}
