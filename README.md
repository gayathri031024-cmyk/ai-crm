Paste **only this** into your GitHub `README.md`. Keep it simple:

````markdown
# AI-First CRM

AI-powered CRM for pharma and medical-device field representatives.

AI-First CRM allows field representatives to manage Healthcare Professional (HCP) interactions using either a structured form or an AI-powered conversational assistant.

## Features

- User authentication with JWT
- HCP management
- Log and manage interactions
- Interaction history and timeline
- Dashboard summaries
- AI-powered CRM assistant
- Sentiment tracking
- REST API with FastAPI

## Tech Stack

**Frontend**
- React
- TypeScript
- Redux Toolkit
- Material UI
- React Hook Form
- Zod
- Vite

**Backend**
- FastAPI
- Python
- SQLAlchemy
- MySQL
- Alembic
- JWT
- LangGraph
- Groq

## Project Structure

```text
ai-crm/
├── frontend/
└── backend/
````

## Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Environment Variables

Create a `.env` file in the backend:

```env
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
CORS_ORIGINS=http://localhost:5173
```

For the frontend:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Status

Active development.

```

**That's enough.** Don't add deployment details, architecture diagrams, or complicated explanations right now.
```
