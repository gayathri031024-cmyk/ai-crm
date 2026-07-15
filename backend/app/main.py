import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.models
from app.api import auth, chat, hcps, interactions
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="AI-First CRM API",
    description="HCP interaction logging with an AI chat assistant (LangGraph + Groq).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(hcps.router, prefix=API_PREFIX)
app.include_router(interactions.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "env": settings.app_env}