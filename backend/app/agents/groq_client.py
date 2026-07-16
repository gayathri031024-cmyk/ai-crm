"""
Thin wrapper around the Groq SDK that automatically falls back from the
primary model to the backup model (and a final safety-net model) if a
call fails (rate limit, timeout, 5xx, decommissioned model, etc).
"""
import logging
from typing import Any

_ALLOWED_MESSAGE_KEYS = {"role", "content", "tool_calls", "tool_call_id", "name"}


def _sanitize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip internal/bookkeeping fields (e.g. model_used) before sending to Groq."""
    return [{k: v for k, v in m.items() if k in _ALLOWED_MESSAGE_KEYS} for m in messages]


from groq import APIConnectionError, APIStatusError, Groq, RateLimitError

from app.core.config import get_settings

logger = logging.getLogger("ai_crm.groq")

RETRYABLE_EXCEPTIONS = (APIConnectionError, APIStatusError, RateLimitError)

# Currently-active model kept as a last-resort fallback, in case both the
# assignment-specified primary and backup models are unavailable/deprecated
# on Groq's side (this has happened before — see console.groq.com/docs/deprecations).
FINAL_FALLBACK_MODEL = "llama-3.1-8b-instant"


class GroqClient:
    def __init__(self):
        settings = get_settings()
        self._client = Groq(api_key=settings.groq_api_key)
        self.primary_model = settings.primary_model
        self.backup_model = settings.backup_model

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> tuple[Any, str]:
        """
        Calls Groq's chat completion endpoint. Tries `primary_model` first,
        then `backup_model`, then a final hardcoded safety-net model.

        Returns (completion_message, model_used).
        """
        models_to_try = [self.primary_model, self.backup_model, FINAL_FALLBACK_MODEL]
        # Avoid trying the same model twice if backup_model happens to already
        # equal the final fallback.
        models_to_try = list(dict.fromkeys(models_to_try))

        last_exc: Exception | None = None

        for i, model in enumerate(models_to_try):
            is_last = i == len(models_to_try) - 1
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=_sanitize_messages(messages),
                    tools=tools,
                    tool_choice="auto" if tools else None,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message, model
            except RETRYABLE_EXCEPTIONS as exc:
                last_exc = exc
                logger.warning(
                    "Groq call failed on model=%s (%s). %s",
                    model,
                    type(exc).__name__,
                    "No more fallbacks." if is_last else "Falling back.",
                )
                if is_last:
                    raise
                continue

        raise last_exc or RuntimeError("Unreachable: all Groq model attempts failed silently.")