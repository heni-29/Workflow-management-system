// src/hooks/useProjectWebSocket.js
/**
 * useProjectWebSocket
 *
 * Opens a WebSocket connection to ws://localhost:8000/ws/projects/<id>/
 * and calls onTaskUpdate(data) whenever the server pushes a task_update event.
 *
 * Auth: the JWT access token is passed as a query param because WebSocket
 * connections can't carry Authorization headers.
 *
 * The hook auto-reconnects on clean close (code 1000/1001) but NOT on auth
 * failure (code 4001) or permanent errors.
 */
import { useEffect, useRef, useCallback } from 'react';

const configuredApiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
const configuredWsBase = (import.meta.env.VITE_WS_BASE_URL || '').replace(/\/+$/, '');

function getWsBase() {
    if (configuredWsBase) {
        return configuredWsBase;
    }

    if (configuredApiBase && /^https?:\/\//.test(configuredApiBase)) {
        const apiUrl = new URL(configuredApiBase);
        const wsProtocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${wsProtocol}//${apiUrl.host}`;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProtocol}//${window.location.host}`;
}

const WS_BASE = getWsBase();
const RECONNECT_DELAY_MS = 3000;

export function useProjectWebSocket(projectId, onTaskUpdate) {
    const wsRef = useRef(null);
    const isMounted = useRef(true);
    const reconnectRef = useRef(null);

    const connect = useCallback(() => {
        if (!projectId || !isMounted.current) return;

        const token = localStorage.getItem('access_token');
        if (!token) return;

        const url = `${WS_BASE}/ws/projects/${projectId}/?token=${token}`;
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log(`[WS] connected to project ${projectId}`);
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'task_update' && onTaskUpdate) {
                    onTaskUpdate(msg);
                }
            } catch (e) {
                console.warn('[WS] failed to parse message', e);
            }
        };

        ws.onerror = (e) => {
            console.warn('[WS] error', e);
        };

        ws.onclose = (event) => {
            console.log(`[WS] closed (code=${event.code})`);
            // Don't reconnect on auth failure or intentional close
            if (!isMounted.current || event.code === 4001) return;

            reconnectRef.current = setTimeout(() => {
                if (isMounted.current) {
                    console.log('[WS] reconnecting…');
                    connect();
                }
            }, RECONNECT_DELAY_MS);
        };
    }, [projectId, onTaskUpdate]);

    useEffect(() => {
        isMounted.current = true;
        connect();

        return () => {
            isMounted.current = false;
            clearTimeout(reconnectRef.current);
            if (wsRef.current) {
                wsRef.current.onclose = null; // prevent reconnect on intentional unmount
                wsRef.current.close();
            }
        };
    }, [connect]);

    return wsRef;
}
