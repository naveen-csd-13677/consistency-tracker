# Personal Consistency Tracker

A full-stack application to help users build and maintain daily habits by tracking completion of duties tied to personal goals, computing consistency metrics, managing progressive difficulty upgrades, and providing AI-powered suggestions.

## Features

- **Goal Management**: Create, track, and manage personal goals with duties
- **Daily Logging**: Simple ✓/✗ interface to log daily habit completion
- **Consistency Metrics**: Daily, weekly, and monthly consistency calculations
- **Upgrade System**: Automatic progression when sustained high consistency is achieved
- **AI Suggestions**: Multi-provider LLM integration (OpenAI, Anthropic, Google, Ollama)
- **Dashboard**: At-a-glance overview with charts and trends
- **Dark/Light Theme**: User-selectable with persisted preference
- **Responsive Design**: Works on desktop and mobile
- **Data Export**: Export all data as CSV or JSON

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Tailwind CSS, Recharts
- **Infrastructure**: Docker Compose

## Quick Start

### Using Docker Compose (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd consistency-tracker

# (Optional) Copy and configure environment variables
cp .env.example .env

# Build and start all services
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requires a PostgreSQL database. Set `DATABASE_URL` environment variable.

#### Frontend

```bash
cd frontend
npm install
npm start
```

Set `REACT_APP_API_URL` to point to the backend (default: `/api` proxied via nginx).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/goals/` | List/Create goals |
| GET/PUT/DELETE | `/api/goals/:id` | Get/Update/Delete goal |
| GET/POST | `/api/duties/` | List/Create duties |
| GET/PUT/DELETE | `/api/duties/:id` | Get/Update/Delete duty |
| GET/POST | `/api/logs/` | List/Upsert daily logs |
| GET | `/api/logs/overview` | Daily overview with consistency % |
| GET | `/api/analytics/weekly` | Weekly consistency analytics |
| GET | `/api/analytics/monthly` | Monthly growth data |
| GET/POST | `/api/upgrades/` | List/Create upgrades |
| GET | `/api/upgrades/readiness` | Upgrade readiness status |
| GET | `/api/suggestions/` | AI suggestions for struggling goals |
| POST | `/api/suggestions/generate` | Force-generate suggestions |
| GET/PUT | `/api/config/` | LLM configuration |
| GET | `/api/export/` | Export data (CSV/JSON) |
| GET | `/api/dashboard/` | Dashboard summary |

## LLM Configuration

The app supports multiple LLM providers for AI-powered suggestions:

1. **OpenAI** - Set `OPENAI_API_KEY`
2. **Anthropic** - Set `ANTHROPIC_API_KEY`
3. **Google Gemini** - Set `GOOGLE_API_KEY`
4. **Ollama** - Local models, set `OLLAMA_BASE_URL` (default: http://localhost:11434)

Configure via the Settings page or environment variables. The app gracefully falls back to rule-based suggestions if no LLM is configured.

## Project Structure

```
consistency-tracker/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API route handlers
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic (consistency, upgrades, LLM)
│   │   ├── config.py         # Application configuration
│   │   ├── database.py       # Database connection
│   │   └── main.py           # FastAPI application entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── pages/            # Page components (Dashboard, Goals, etc.)
│   │   ├── api.js            # API client
│   │   ├── App.js            # Main app with routing
│   │   └── index.js          # Entry point
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```
