# Workflow - Project Management System

A modern Django-based project management application with task tracking, activity logging, and interactive dashboards.

## Features

- **Project Management**: Create and manage multiple projects with team members
- **Task Tracking**: Track tasks with status (To Do, In Progress, Review, Done) and priority levels
- **Interactive Dashboards**: Visualize task distribution with Plotly charts
- **Activity Feed**: Timeline view of all project activities
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- **Secure Authentication**: Login-only access with CSRF protection

## Tech Stack

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Frontend**: HTML, Tailwind CSS 2.2.19
- **Visualization**: Plotly 6.3.1
- **API**: Django REST Framework 3.16.1

## Installation

### Prerequisites

- Python 3.13
- PostgreSQL (optional, can use SQLite)
- pipenv (recommended) or pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/heni-29/Workflow-management-system
   cd workflow
   ```

2. **Install dependencies**
   
   Using pipenv (recommended):
   ```bash
   pipenv install
   pipenv shell
   ```
   
   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=1
   POSTGRES_HOST=sqlite  # Use 'sqlite' for SQLite, or 'localhost' for PostgreSQL
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```
   
   Or use the default credentials provided below.

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:8000`

## Default Login Credentials

- **Username**: `djangoadmin`
- **Password**: `12admin34`

## Usage

### Projects
- View all projects on the homepage
- Click on a project card to see details
- Access project dashboard to view task statistics

### Tasks
- Navigate to "Tasks" to see all tasks across projects
- Create new tasks with the "Create Task" button
- Tasks are color-coded by status:
  - Gray: To Do
  - Blue: In Progress
  - Yellow: Review
  - Green: Done

### Activities
- View the activity timeline to track all changes
- See who made changes and when

## Project Structure

```
workflow/
├── backend/          # Django settings and configuration
├── projects/         # Projects app
├── tasks/            # Tasks app
├── activities/       # Activity logging app
├── users/            # User authentication
├── templates/        # HTML templates
│   ├── base.html
│   ├── projects/
│   ├── tasks/
│   ├── activities/
│   └── registration/
├── manage.py
├── requirements.txt
└── Pipfile
```

## Development

### Database Options

**SQLite (Default for Development)**
- Set `POSTGRES_HOST=sqlite` in `.env` <br>
- No additional setup required

**PostgreSQL (Recommended for Production)**
- Install PostgreSQL
- Create a database named `workflow_db`
- Update `.env`:
  ```env
  POSTGRES_HOST=localhost
  ```
- Update `backend/settings.py` with your PostgreSQL credentials if needed

### Running Tests

```bash
python manage.py test
```