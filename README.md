# Workflow - Project Management System

A full-stack project management app built with Django REST Framework and React.

## Tech Stack

- **Backend** - Django, Django REST Framework, Django Channels (WebSockets)
- **Auth** - JWT via `djangorestframework-simplejwt`
- **Frontend** - React + Vite, Recharts, Axios, React Router
- **Database** - PostgreSQL (SQLite for dev)
- **Real-time** - Django Channels + Daphne (ASGI)

## Getting Started

### 1. Clone & configure

```bash
git clone https://github.com/heni-29/Workflow-management-system
cd workflow
```

Create a `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
POSTGRES_HOST=sqlite
```

### 2. Backend

```bash
pip install -r requirements.txt
python manage.py migrate
```

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Run

```bash
# Terminal 1 - Django (use Daphne for WebSocket support)
daphne -p 8000 backend.asgi:application

# Terminal 2 - React
cd frontend && npm run dev
```

Open **http://localhost:3000**

> The React app proxies `/api/*` and `/ws/*` requests to the Django backend at port 8000.

## Default Login

| Username | Password |
|---|---|
| `djangoadmin` | `12admin34` |

## Features

- Projects and tasks with status, priority, assignees, and due dates
- Real-time task updates via WebSocket - changes push to all connected clients instantly
- JWT auth with silent token refresh
- Dashboard with Recharts bar and pie charts
- Paginated activity feed
- Filterable task table

## WebSocket

Connected clients on a project page receive live task updates automatically:

```
ws://localhost:8000/ws/projects/<id>/?token=<jwt>
```

Auth is handled via the `?token=` query param since WebSocket connections can't send headers. The Project Detail page shows a Live/Offline indicator and flashes updated rows.

## API Endpoints

All require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/token/` | Login |
| `POST` | `/api/auth/token/refresh/` | Refresh token |
| `GET/POST` | `/api/projects/` | List / create projects |
| `GET` | `/api/projects/:id/stats/` | Task breakdown by status |
| `GET/POST` | `/api/tasks/` | List / create tasks |
| `PATCH` | `/api/tasks/:id/set_status/` | Update status (broadcasts via WS) |
| `GET` | `/api/activities/` | Activity log |
| `GET` | `/api/users/me/` | Current user |

Browsable API at `http://localhost:8000/api/`

## Database

Set `POSTGRES_HOST=sqlite` in `.env` for local dev (no setup needed).

For PostgreSQL:
```env
POSTGRES_HOST=localhost
POSTGRES_DB=workflow_db
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password
```

## Seed Data

```bash
python manage.py populate_data
```