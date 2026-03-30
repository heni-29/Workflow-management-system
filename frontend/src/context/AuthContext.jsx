// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const GUEST_USER = {
    id: null,
    username: 'guest',
    first_name: 'Guest',
    last_name: '',
    role: 'Viewer',
};

export function AuthProvider({ children }) {
    const [user] = useState(GUEST_USER);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(false);
    }, []);

    const login = async () => GUEST_USER;

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
