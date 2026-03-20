# Workflow — Project Management System

A full-stack project management application with a **Django REST Framework** backend and a **React** (Vite) frontend, featuring JWT authentication, interactive Recharts dashboards, and a clean dark-mode UI.

---

## Features

- **Project Management** — Create and manage projects with team members and progress tracking
- **Task Tracking** — Tasks with status (To Do → In Progress → Review → Done), priority levels, assignees, and due dates
- **Interactive Dashboard** — Recharts bar + donut charts for task distribution across projects and statuses
- **Activity Feed** — Paginated timeline of all project changes with color-coded action types
- **JWT Authentication** — Stateless Bearer token auth with silent refresh; 8-hour access tokens, 7-day refresh tokens
- **REST API** — Full DRF ViewSet API with filtering, search, ordering, and pagination
- **Dark-mode UI** — Premium design system built from scratch in vanilla CSS

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.2.7 · Django REST Framework 3.16.1 |
| **Auth** | `djangorestframework-simplejwt` (JWT Bearer tokens) |
| **Database** | PostgreSQL (SQLite fallback for dev) |
| **CORS** | `django-cors-headers` |
| **Frontend** | React 18 · Vite (port 3000) |
| **Charts** | Recharts |
| **HTTP client** | Axios (with JWT interceptors + auto-refresh) |
| **Routing** | React Router v7 |
| **Icons** | Lucide React |

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL (or use SQLite for dev)

### 1 - Clone & configure

```bash
git clone https://github.com/heni-29/Workflow-management-system
cd workflow
```

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=1
POSTGRES_HOST=sqlite        # 'sqlite' for SQLite, 'localhost' for PostgreSQL
```

### 2 - Backend setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # or use default credentials below
```

### 3 - Frontend setup

```bash
cd frontend
npm install
```

### 4 - Run the stack

```bash
# Terminal 1 — Django API (http://localhost:8000)
python manage.py runserver 8000

# Terminal 2 — React dev server (http://localhost:3000)
cd frontend && npm run dev
```

Open **http://localhost:3000** — Vite proxies all `/api` requests to Django on port 8000.

---

## Default Login

| Field | Value |
|---|---|
| Username | `djangoadmin` |
| Password | `12admin34` |

---

## REST API Endpoints

All endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/token/` | Login → receive access + refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Exchange refresh token for new access token |
| `POST` | `/api/auth/token/verify/` | Verify a token |
| `GET` | `/api/projects/` | List all projects |
| `POST` | `/api/projects/` | Create a project |
| `GET` | `/api/projects/:id/` | Get a single project |
| `PATCH` | `/api/projects/:id/` | Update a project |
| `GET` | `/api/projects/:id/tasks/` | All tasks for a project |
| `GET` | `/api/projects/:id/stats/` | Task counts by status |
| `GET` | `/api/tasks/` | List tasks (filter by `status`, `project`, `priority`, `assignee`) |
| `POST` | `/api/tasks/` | Create a task |
| `PATCH` | `/api/tasks/:id/` | Update a task |
| `PATCH` | `/api/tasks/:id/set_status/` | Quick status change |
| `GET` | `/api/tasks/my/` | Tasks assigned to the current user |
| `GET` | `/api/activities/` | Paginated activity log |
| `GET` | `/api/users/me/` | Current authenticated user |

The **browsable DRF API** is also available at `http://localhost:8000/api/` for manual exploration.

---

## Project Structure

```
workflow/
├── backend/              # Django settings · WSGI/ASGI
├── api/                  # DRF ViewSets, serializers, JWT URLs
├── projects/             # Project model, views, URLs
├── tasks/                # Task model (status/priority choices)
├── activities/           # ActivityLog model (JSONField detail)
├── users/                # Custom User model · management commands
├── templates/            # Legacy Django HTML templates
├── requirements.txt
├── manage.py
└── frontend/             # Vite + React SPA
    ├── vite.config.js    # port 3000, /api proxy → :8000
    └── src/
        ├── api/
        │   └── client.js         # Axios + JWT interceptors + auto-refresh
        ├── context/
        │   └── AuthContext.jsx   # Login / logout / persistent session
        ├── components/
        │   ├── Sidebar.jsx
        │   ├── Badges.jsx        # StatusBadge, PriorityBadge
        │   └── ProtectedRoute.jsx
        ├── pages/
        │   ├── LoginPage.jsx
        │   ├── DashboardPage.jsx
        │   ├── ProjectsPage.jsx
        │   ├── ProjectDetailPage.jsx
        │   ├── TasksPage.jsx
        │   └── ActivityPage.jsx
        ├── utils/time.js         # formatRelative, formatDate
        └── index.css             # Design system (dark theme tokens)
```

---

## Database Options

**SQLite** (default for development)
- Set `POSTGRES_HOST=sqlite` in `.env` — no extra setup needed

**PostgreSQL** (recommended for production)
```env
POSTGRES_HOST=localhost
POSTGRES_DB=workflow_db
POSTGRES_USER=workflow_user
POSTGRES_PASSWORD=your-password
POSTGRES_PORT=5432
```

---

## Running Tests

```bash
python manage.py test
```

---

## Seed Data

Populate the database with realistic CS student projects:

```bash
python manage.py populate_data
```