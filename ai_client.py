"""
Centralized OpenRouter AI client module.

Uses the official OpenAI Python SDK pointed at OpenRouter's API.
Provides model fallback chain, retry logic, and robust JSON extraction.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError, AuthenticationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

logger = logging.getLogger("episteme.ai_client")

# ── OpenRouter Configuration ──────────────────────────────────────────────────

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Free model fallback chain (tried in order)
MODEL_FALLBACK_CHAIN: List[str] = [
    # User requested models
    "deepseek/deepseek-r1-0528:free",
    "qwen/qwen3-235b-a22b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.2-24b-instruct:free",
    # Empirically verified active OpenRouter free models
    "google/gemma-4-26b-a4b-it:free",
    "openai/gpt-oss-20b:free",
    "inclusionai/ling-3.0-flash:free",
    "cohere/north-mini-code:free",
]

DEFAULT_MODEL = MODEL_FALLBACK_CHAIN[0]


def _get_api_key() -> str:
    """Return the OPENROUTER_API_KEY or raise immediately."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. "
            "Add it to your .env file or export it as an environment variable."
        )
    return key


def get_openrouter_client() -> OpenAI:
    """
    Create and return an OpenAI client configured for OpenRouter.
    Raises RuntimeError if OPENROUTER_API_KEY is missing.
    """
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=_get_api_key(),
        default_headers={
            "HTTP-Referer": "https://episteme.app",
            "X-Title": "EPISTEME Research Engine",
        },
    )


# ── JSON Extraction ───────────────────────────────────────────────────────────

def extract_json_from_response(text: str) -> str:
    """
    Extract clean JSON from an LLM response.

    Handles:
      - DeepSeek R1 <think>…</think> reasoning blocks
      - Markdown ```json … ``` fences
      - Raw JSON objects/arrays
    """
    if not text:
        return "{}"

    # 1. Strip <think>…</think> blocks (DeepSeek R1 reasoning)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # 2. Strip markdown json fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # 3. Find first { or [ and extract to matching bracket
    for i, ch in enumerate(cleaned):
        if ch == "{":
            depth = 0
            for j in range(i, len(cleaned)):
                if cleaned[j] == "{":
                    depth += 1
                elif cleaned[j] == "}":
                    depth -= 1
                if depth == 0:
                    return cleaned[i : j + 1]
        elif ch == "[":
            depth = 0
            for j in range(i, len(cleaned)):
                if cleaned[j] == "[":
                    depth += 1
                elif cleaned[j] == "]":
                    depth -= 1
                if depth == 0:
                    return cleaned[i : j + 1]

    # 4. Last resort: return whatever we have
    return cleaned


# ── Core Completion Function ──────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=15),
    retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
    reraise=True,
)
def _call_openrouter(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    json_mode: bool = True,
) -> str:
    """
    Make a single chat completion call to OpenRouter with tenacity retries.
    Returns the raw assistant message content.
    """
    kwargs: Dict[str, Any] = {
        "messages": messages,
        "model": model,
        "temperature": temperature,
    }
    # Request structured JSON output when requested
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    json_mode: bool = True,
    model: Optional[str] = None,
) -> str:
    """
    High-level completion function with automatic model fallback.

    Tries each model in the fallback chain until one succeeds.
    Returns extracted JSON string when json_mode=True, raw text otherwise.

    Raises on all errors — never returns silent fallback data.
    """
    client = get_openrouter_client()

    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    models_to_try = [model] if model else MODEL_FALLBACK_CHAIN
    last_error: Optional[Exception] = None

    for m in models_to_try:
        try:
            logger.info(f"Calling OpenRouter model: {m}")
            raw = _call_openrouter(
                client=client,
                model=m,
                messages=messages,
                temperature=temperature,
                json_mode=json_mode,
            )
            if json_mode:
                return extract_json_from_response(raw)
            return raw

        except AuthenticationError as e:
            logger.error(f"Authentication failed for model {m}: {e}")
            raise RuntimeError(
                f"OpenRouter authentication failed. Check your OPENROUTER_API_KEY. "
                f"Provider error: {e}"
            ) from e

        except RateLimitError as e:
            logger.warning(f"Rate limited on model {m}: {e}")
            last_error = e
            continue  # try next model

        except APITimeoutError as e:
            logger.warning(f"Timeout on model {m}: {e}")
            last_error = e
            continue

        except APIConnectionError as e:
            logger.warning(f"Connection error on model {m}: {e}")
            last_error = e
            continue

        except APIError as e:
            logger.warning(f"API error on model {m} (status {e.status_code}): {e}")
            last_error = e
            continue  # try next model

        except Exception as e:
            logger.error(f"Unexpected error on model {m}: {e}")
            last_error = e
            continue

    # All models exhausted
    raise RuntimeError(
        f"All OpenRouter models failed. Last error: {last_error}"
    )
