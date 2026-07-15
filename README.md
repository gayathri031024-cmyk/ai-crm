# AI-First CRM

An AI-first CRM for pharma/med-device field reps to log **HCP (Healthcare Professional) interactions** either through a structured form or a natural-language chat assistant (LangGraph + Groq), with a dashboard and full interaction timeline.

- **Backend:** FastAPI + SQLAlchemy + MySQL + Alembic, JWT auth, LangGraph agent with tool-calling via Groq
- **Frontend:** Vite + React 19 + TypeScript, Redux Toolkit, MUI, React Hook Form + Zod

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Database & Migrations](#database--migrations)
5. [Frontend Setup](#frontend-setup)
6. [Running Everything](#running-everything)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Sample Requests & Responses](#sample-requests--responses)
10. [Postman Collection](#postman-collection)
11. [Project Structure](#project-structure)
12. [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────┐        HTTPS / JSON        ┌──────────────────────────┐
│   React Frontend     │ ───────────────────────────▶│      FastAPI Backend     │
│  (Vite, MUI, RTK)     │◀─────────────────────────── │  /api/v1/*                │
└─────────────────────┘                              └───────────┬──────────────┘
                                                                   │
                                                    ┌──────────────┼───────────────┐
                                                    │              │               │
                                              ┌─────▼─────┐ ┌──────▼──────┐ ┌──────▼──────┐
                                              │   MySQL    │ │  LangGraph  │ │  Groq API   │
                                              │ (SQLAlchemy│ │  CRM Agent  │ │ (LLM calls) │
                                              │  + Alembic)│ │ (tool-use)  │ │             │
                                              └───────────┘ └─────────────┘ └─────────────┘
```

Two ways to log an interaction, one data model:

- **Structured Form** → `POST /api/v1/interactions` directly.
- **AI Chat** → `POST /api/v1/chat` → LangGraph agent resolves the HCP, extracts fields from natural language, and calls the same interaction-logging tool under the hood. Every interaction created this way is tagged `created_via: "ai_chat"` and shows a badge on the timeline.

## Prerequisites

| Tool          | Version   |
|---------------|-----------|
| Python        | 3.11+     |
| Node.js       | 20+       |
| MySQL         | 8.x       |
| npm           | 10+       |
| A Groq API key| [console.groq.com](https://console.groq.com) |

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL, JWT_SECRET_KEY, GROQ_API_KEY at minimum
```

## Database & Migrations

You have two options — pick one.

**Option A — apply the raw schema directly (fastest for local dev):**

```bash
mysql -u root -p < docs/schema.sql
```

**Option B — use Alembic migrations** (recommended if you'll evolve the schema):

```bash
cd backend
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

> The `DATABASE_URL` in `.env` must point to an existing empty database (e.g. `ai_crm`) before running either option. Option A's `docs/schema.sql` also creates the database itself via `CREATE DATABASE IF NOT EXISTS ai_crm`.

## Frontend Setup

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_BASE_URL=http://localhost:8000/api/v1
```

> The Vite dev server also proxies `/api/*` to `http://localhost:8000` (see `vite.config.ts`), so the app works even without setting `VITE_API_BASE_URL` explicitly during local development.

## Running Everything

```bash
# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

- Frontend: http://localhost:5173
- Backend docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

First run: open http://localhost:5173/register to create a rep account, then log in.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy MySQL connection string | `mysql+pymysql://crm_user:crm_password@localhost:3306/ai_crm` |
| `JWT_SECRET_KEY` | Secret used to sign JWTs (**required**, no default) | — |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `GROQ_API_KEY` | API key for Groq (powers the chat assistant) | — |
| `PRIMARY_MODEL` | Primary Groq model | `gemma2-9b-it` |
| `BACKUP_MODEL` | Fallback Groq model | `llama-3.3-70b-versatile` |
| `APP_ENV` | `development` \| `production` | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `LOG_LEVEL` | Python logging level | `INFO` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend API | `http://localhost:8000/api/v1` |

## API Reference

All endpoints are prefixed with `/api/v1` and (except auth) require `Authorization: Bearer <access_token>`.

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create a rep account, returns tokens |
| POST | `/auth/login` | Log in, returns tokens |
| POST | `/auth/refresh` | Exchange a refresh token for a new pair |
| GET | `/auth/me` | Current authenticated user |
| GET | `/hcps` | List HCPs (paginated, searchable, filterable) |
| POST | `/hcps` | Create an HCP |
| GET | `/hcps/{id}` | Get one HCP |
| PUT | `/hcps/{id}` | Update an HCP |
| DELETE | `/hcps/{id}` | Delete an HCP |
| GET | `/interactions` | List interactions (paginated, filterable by HCP, type, sentiment, date range, search) |
| POST | `/interactions` | Log a new interaction |
| GET | `/interactions/dashboard/summary` | Dashboard summary counts |
| GET | `/interactions/{id}` | Get one interaction |
| PUT | `/interactions/{id}` | Update an interaction |
| DELETE | `/interactions/{id}` | Delete an interaction |
| GET | `/interactions/{id}/history` | Field-level change history |
| POST | `/chat` | Send a message to the AI assistant |
| GET | `/history` | List past chat conversations |
| GET | `/history/{conversation_id}` | Full message history for one conversation |

Full interactive docs (request/response schemas, try-it-out) are always available at `/docs` while the backend is running.

## Sample Requests & Responses

### Register

`POST /api/v1/auth/register`
```json
{
  "email": "rep@example.com",
  "password": "SecurePass123",
  "full_name": "Asha Rao",
  "territory": "Hyderabad South"
}
```
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "b1e2c3d4-...",
    "email": "rep@example.com",
    "full_name": "Asha Rao",
    "role": "rep",
    "is_active": true,
    "territory": "Hyderabad South",
    "created_at": "2026-07-14T09:00:00"
  }
}
```

### Log an Interaction (form)

`POST /api/v1/interactions`
```json
{
  "hcp_id": "3f9a2b10-...",
  "interaction_type": "visit",
  "visit_date": "2026-07-14T10:30:00",
  "follow_up_date": "2026-07-21",
  "discussion_summary": "Discussed new dosing guidance for Cardiozen.",
  "products_discussed": ["Cardiozen"],
  "samples_given": 10,
  "sentiment": "positive",
  "next_action": "Send updated clinical trial data",
  "notes": "Very receptive, wants a lunch-and-learn next month.",
  "created_via": "form"
}
```
```json
{
  "id": "8c1d2e3f-...",
  "hcp_id": "3f9a2b10-...",
  "user_id": "b1e2c3d4-...",
  "interaction_type": "visit",
  "visit_date": "2026-07-14T10:30:00",
  "follow_up_date": "2026-07-21",
  "discussion_summary": "Discussed new dosing guidance for Cardiozen.",
  "products_discussed": ["Cardiozen"],
  "samples_given": 10,
  "sentiment": "positive",
  "next_action": "Send updated clinical trial data",
  "notes": "Very receptive, wants a lunch-and-learn next month.",
  "created_via": "form",
  "created_at": "2026-07-14T10:35:12",
  "updated_at": "2026-07-14T10:35:12"
}
```

### Chat (AI-logged interaction)

`POST /api/v1/chat`
```json
{
  "message": "Log a visit with Dr. Mehta today, discussed Cardiozen dosing, gave 10 samples, positive sentiment",
  "conversation_id": null
}
```
```json
{
  "conversation_id": "d4e5f6a7-...",
  "reply": "Logged your visit with Dr. Mehta — Cardiozen dosing discussed, 10 samples given, sentiment marked positive. Anything else you'd like to add?",
  "messages": [
    {
      "id": "m1...",
      "role": "user",
      "content": "Log a visit with Dr. Mehta today, discussed Cardiozen dosing, gave 10 samples, positive sentiment",
      "tool_name": null,
      "tool_output": null,
      "model_used": null,
      "created_at": "2026-07-14T10:40:00"
    },
    {
      "id": "m2...",
      "role": "tool",
      "content": "",
      "tool_name": "log_interaction",
      "tool_output": { "interaction_id": "8c1d2e3f-...", "status": "created" },
      "model_used": null,
      "created_at": "2026-07-14T10:40:02"
    },
    {
      "id": "m3...",
      "role": "assistant",
      "content": "Logged your visit with Dr. Mehta — Cardiozen dosing discussed, 10 samples given, sentiment marked positive. Anything else you'd like to add?",
      "tool_name": null,
      "tool_output": null,
      "model_used": "gemma2-9b-it",
      "created_at": "2026-07-14T10:40:02"
    }
  ]
}
```

### Dashboard Summary

`GET /api/v1/interactions/dashboard/summary?mine_only=true`
```json
{
  "todays_visits": 4,
  "pending_follow_ups": 7,
  "total_interactions": 132,
  "positive_sentiment_pct": 68
}
```

## Postman Collection

A ready-to-import Postman collection with all endpoints above (including pre-filled example bodies and a collection-level Bearer token variable that auto-fills after login) is at:

```
docs/AI-First-CRM.postman_collection.json
```

Import it, set the `base_url` collection variable (defaults to `http://localhost:8000/api/v1`), run **Auth → Login** or **Auth → Register** once, and the `access_token` variable populates automatically for every subsequent request via a small test script on those two requests.

## Project Structure

```
ai-crm/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agent, state, Groq client
│   │   ├── api/              # FastAPI routers (auth, hcps, interactions, chat)
│   │   ├── core/              # config, security, dependencies, error handlers
│   │   ├── database/         # SQLAlchemy session/engine
│   │   ├── middleware/       # request logging
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── repositories/     # data-access layer
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── services/          # business logic
│   │   ├── tools/             # LangGraph tool definitions + registry
│   │   └── utils/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # axios client + endpoint wrappers
│   │   ├── app/                # Redux store + typed hooks
│   │   ├── components/       # forms, chat, dashboard, timeline, common
│   │   ├── features/          # Redux slices (auth, interactions, hcps, chat, ui)
│   │   ├── layout/             # Sidebar, Navbar, MainLayout
│   │   ├── pages/               # route-level pages
│   │   ├── routes/             # React Router config + ProtectedRoute
│   │   ├── theme/              # MUI theme
│   │   └── types/              # shared TS types mirroring backend schemas
│   └── package.json
├── docs/
│   ├── schema.sql
│   └── AI-First-CRM.postman_collection.json
└── README.md
```

## Troubleshooting

- **401 on every request after login works fine at first** — your access token expired; the frontend auto-refreshes using the refresh token via an axios interceptor, so this should be transparent. If it isn't, check that `JWT_SECRET_KEY` didn't change between backend restarts (that invalidates all existing tokens).
- **CORS errors in the browser console** — make sure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`.
- **Chat replies are empty or error out** — verify `GROQ_API_KEY` is set and valid, and that your Groq account has access to the configured `PRIMARY_MODEL`.
- **`ModuleNotFoundError` on backend start** — reinstall dependencies with `pip install -r requirements.txt` inside an active virtualenv.
