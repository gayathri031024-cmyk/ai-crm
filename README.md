# AI-First CRM — HCP Module (Log Interaction Screen)

An AI-first CRM for life-science field representatives. Reps log interactions with
Healthcare Professionals (HCPs) in **either** of two ways on a single screen:

1. a **structured form**, or
2. a **conversational AI assistant** (chat) powered by a **LangGraph** agent and a **Groq LLM**.

Both paths write to the same MySQL database, so a visit logged by chat shows up in the
form list and the timeline, and vice versa.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Redux Toolkit, Material UI, React Hook Form, Zod, Vite |
| Font | Google **Inter** |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, JWT auth |
| AI agent | **LangGraph** (`StateGraph`) |
| LLM | **Groq** — `llama-3.3-70b-versatile` (primary), `openai/gpt-oss-120b` (backup) |
| Database | **MySQL** |

### A note on the LLM choice

The assignment suggests `gemma2-9b-it`. Groq **deprecated and removed `gemma2-9b-it`
(October 2025)**, so calls to it now fail. As the brief also allows
`llama-3.3-70b-versatile`, this project uses it as the primary model. The model names are
configurable through `PRIMARY_MODEL` and `BACKUP_MODEL` in `backend/.env`, and the client
automatically falls back to the backup model if a call fails.

## How the LangGraph agent works

The agent is a LangGraph `StateGraph` loop:

```
START -> agent -> (tool calls?) -> tools -> agent -> ... -> END
```

The `agent` node sends the conversation and the tool schemas to Groq. If the model asks
for a tool, the `tools` node runs it against the real database and feeds the result back
to the `agent` node so it can confirm the action or ask a clarifying question. A hard cap
of 4 iterations prevents infinite tool loops.

### The 5 tools

| Tool | What it does |
|---|---|
| `log_interaction` | Turns a natural-language description (e.g. *"Met Dr. Sharma today, discussed insulin, gave 5 samples, follow up next Friday"*) into a structured interaction: HCP, type, date, summary, products, samples, sentiment, follow-up and next action. The LLM does the entity extraction and summarization, and resolves relative dates like "today" to ISO dates. Can create a new HCP if one is not found. |
| `edit_interaction` | Modifies an already-logged interaction (e.g. *"Actually it was 10 samples"*, *"Change the sentiment to positive"*). Defaults to the most recent interaction for the named HCP. Changes are recorded in the interaction history. |
| `search_hcp` | Finds HCPs by name, hospital, city or specialization. |
| `schedule_follow_up` | Sets or moves the follow-up date on an existing interaction. |
| `generate_visit_summary` | Summarizes recent visits with an HCP so the rep can prepare for the next meeting. |

## Project Structure

```
ai-crm/
├── backend/
│   ├── app/
│   │   ├── agents/        # LangGraph graph, state, Groq client (with fallback)
│   │   ├── tools/         # The 5 agent tools, schemas and registry
│   │   ├── api/           # FastAPI routers: auth, hcps, interactions, chat
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Database access
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── core/          # Config, security, dependencies, error handlers
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/    # chat, forms, timeline, dashboard
│       ├── features/      # Redux slices (auth, chat, hcp, interactions, ui)
│       ├── pages/         # Login, Register, Dashboard, Log Interaction, Timeline
│       └── api/           # API client modules
└── docs/                  # schema.sql and Postman collection
```

## Run Locally

### Prerequisites

- Python 3.11
- Node.js 18+
- MySQL 8
- A Groq API key — create one at https://console.groq.com

### 1. Database (MySQL)

```sql
CREATE DATABASE ai_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crm_user'@'localhost' IDENTIFIED BY 'crm_password';
GRANT ALL PRIVILEGES ON ai_crm.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# Edit .env: set GROQ_API_KEY and a long random JWT_SECRET_KEY

alembic upgrade head               # creates all tables
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

> `docs/schema.sql` is an optional plain-SQL copy of the schema. Alembic is the
> recommended way to create the tables.

### 3. Frontend

```bash
cd frontend
cp .env.example .env               # Windows: copy .env.example .env
npm install
npm run dev
```

App: http://localhost:5173

### 4. Try it

1. Register an account, then log in.
2. Open **Log Interaction**. Use the form on the left or the AI assistant on the right.
3. In the chat, try:
   - `Met Dr. Sharma today, discussed insulin, gave 5 samples, follow up next Friday`
   - `Actually it was 10 samples`
   - `Find HCPs in Mumbai`
   - `Move the follow-up for Dr. Sharma to next Monday`
   - `Summarize my recent visits with Dr. Sharma`

## Environment Variables

**`backend/.env`** (see `backend/.env.example`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | MySQL connection string, e.g. `mysql+pymysql://crm_user:crm_password@localhost:3306/ai_crm` |
| `JWT_SECRET_KEY` | Long random secret for signing tokens |
| `GROQ_API_KEY` | Your Groq API key |
| `PRIMARY_MODEL` | Default `llama-3.3-70b-versatile` |
| `BACKUP_MODEL` | Default `openai/gpt-oss-120b` |
| `CORS_ORIGINS` | Default `http://localhost:5173` |

**`frontend/.env`**

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Default `http://localhost:8000/api/v1` |

## API Overview

All routes are under `/api/v1`.

- **Auth:** `POST /register`, `POST /login`, `POST /refresh`, `GET /me`
- **HCPs:** `POST /hcps`, `GET /hcps`, `GET/PUT/DELETE /hcps/{id}`
- **Interactions:** `POST /interactions`, `GET /interactions`, `GET/PUT/DELETE /interactions/{id}`, `GET /interactions/{id}/history`, `GET /interactions/dashboard/summary`
- **AI chat:** `POST /chat`, `GET /history`, `GET /history/{conversation_id}`

A Postman collection is available in `docs/`.