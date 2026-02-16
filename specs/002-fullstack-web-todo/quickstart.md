# Quickstart: Phase 2 — Full Stack Web Todo

**Feature Branch**: `002-fullstack-web-todo`
**Created**: 2026-01-06

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (Neon managed)
- Git

## Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start development server
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host/database
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Verify Installation

1. Backend health check: http://localhost:8000/health
2. Frontend: http://localhost:3000
3. API docs: http://localhost:8000/docs

## Common Commands

```bash
# Backend
cd backend
alembic upgrade head
pytest

# Frontend
cd frontend
npm run build
npm run test
```
