# AI-First CRM

An AI-first CRM for pharma/med-device field reps to log **HCP (Healthcare Professional) interactions** either through a structured form or a natural-language chat assistant (LangGraph + Groq), with a dashboard and full interaction timeline.

- **Backend:** FastAPI + SQLAlchemy + MySQL + Alembic, JWT auth, LangGraph agent with tool-calling via Groq
- **Frontend:** Vite + React 19 + TypeScript, Redux Toolkit, MUI, React Hook Form + Zod

---

## Table of Contents

1. [Architecture](#architecture)
2. [LangGraph Agent & Tools](#langgraph-agent--tools)
3. [Prerequisites](#prerequisites)
4. [Backend Setup](#backend-setup)
5. [Database & Migrations](#database--migrations)
6. [Frontend Setup](#frontend-setup)
7. [Running Everything](#running-everything)
8. [Environment Variables](#environment-variables)
9. [API Reference](#api-reference)
10. [Sample Requests & Responses](#sample-requests--responses)
11. [Postman Collection](#postman-collection)
12. [Project Structure](#project-structure)
13. [Troubleshooting](#troubleshooting)

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

## LangGraph Agent & Tools

The LangGraph agent (`backend/app/agents/graph.py`) runs a loop: it sends the full conversation history plus all 5 tool schemas to Groq on every turn. If the model responds with a tool call, the agent executes it against the database via `app/tools/crm_tools.py`, appends the result as a tool message, and loops back to the model — up to `MAX_TOOL_ITERATIONS` (4) times — so the model can react to what happened (e.g. confirm a save, or ask a clarifying question) before producing its final natural-language reply. This lets a rep either fill out the structured form or just describe a visit conversationally, with both paths landing in the same `interactions` table.

| Tool | Purpose |
|---|---|
| `log_interaction` | Creates a new structured interaction record from natural language. The LLM extracts the HCP name, interaction type, date, products discussed, samples given, sentiment, follow-up date, and next action from the user's free-text message, resolves relative dates ("today", "next Friday") into ISO dates itself, and calls this tool with the structured fields. The tool resolves the HCP by name (asking for clarification if ambiguous or not found) and writes the interaction. |
| `edit_interaction` | Modifies an already-logged interaction (e.g. "Actually it was 10 samples, not 5"). Resolves which interaction to edit either by an explicit interaction ID or by finding the user's most recent interaction with the mentioned HCP (or their most recent interaction overall if no HCP is named), then applies only the fields the user actually mentioned changing. |
| `search_hcp` | Searches HCPs by name, hospital, city, or specialization and returns matching records. |
| `schedule_follow_up` | Sets or moves the follow-up date on an existing interaction, resolving the target interaction the same way `edit_interaction` does. |
| `generate_visit_summary` | Produces a readable recap of recent interactions for a given HCP, most recent first. |

All five tool schemas are Pydantic models (`app/tools/schemas.py`) that double as the JSON schema sent to Groq and as runtime validation when a tool call comes back — see `app/tools/registry.py` for how they're wired together and dispatched by name.

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
| `PRIMARY_MODEL` | Primary Groq model | `llama-3.3-70b-versatile` |
| `BACKUP_MODEL` | Fallback Groq model | `openai/gpt-oss-120b` |
| `APP_ENV` | `development` \| `production` | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `LOG_LEVEL` | Python logging level | `INFO` |

> **Note on model choice:** The original spec for this project referenced `gemma2-9b-it`.
> That model was deprecated by Groq on Oct 8, 2025, and is no longer callable via their API.
> This project uses `llama-3.3-70b-versatile` as the primary model instead (with
> `openai/gpt-oss-120b` as an automatic fallback on rate limits/errors — see
> `app/agents/groq_client.py`), since it's a current, actively-supported Groq model with
> reliable multi-tool function-calling support.

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
      "model_used": "llama-3.3-70b-versatile",
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
- **Chat tool-calling seems inconsistent or a tool never fires** — check the `model_used` column in `ai_messages` for that turn, and check backend logs for `ai_crm.groq` entries (`groq.request`/`groq.response`) to see which model actually served the request and whether it returned any `tool_calls`. Groq periodically deprecates models (see the note above), which can silently degrade tool-calling quality if `PRIMARY_MODEL` becomes stale.
- **`ModuleNotFoundError` on backend start** — reinstall dependencies with `pip install -r requirements.txt` inside an active virtualenv.