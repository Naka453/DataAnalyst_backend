from __future__ import annotations

import json
import re
from typing import Any, Dict

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from app.core.config import settings


# -------- Helpers --------

def _extract_json_text(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return s

    # ```json ... ``` fence авч хаях
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"\s*```$", "", s).strip()

    # эхний { ... сүүлийн } хүртэл
    i = s.find("{")
    j = s.rfind("}")
    if i != -1 and j != -1 and j > i:
        return s[i : j + 1].strip()

    return s


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    return json.loads(_extract_json_text(raw))


def _is_quota_error(e: Exception) -> bool:
    # google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED
    return isinstance(e, genai_errors.ClientError) and getattr(e, "status_code", None) == 429


# -------- Client (create once) --------

_client: genai.Client = genai.Client(api_key=settings.gemini_api_key)


# -------- Public API --------

def llm_json(prompt: str) -> Dict[str, Any]:
    """
    google.genai → JSON only (sanitize + retry)
    429 quota үед raise хийнэ (chat.py дээр fallback intent рүү шилжинэ)
    """
    try:
        raw = _client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        ).text

        raw = (raw or "").strip()
        if not raw:
            raise ValueError("Gemini returned empty response (json)")

        try:
            return _safe_json_loads(raw)
        except Exception as e1:
            retry_prompt = (
                prompt
                + "\n\n"
                + "АНХААР: ӨӨР ТЕКСТ БИЧИХГҮЙ. ЗӨВХӨН НЭГ JSON ОБЪЕКТ БУЦАА. "
                  "Markdown code fence (```), тайлбар өгүүлбэр, нэмэлт тэмдэгт бичихийг хориглоно."
            )

            raw2 = _client.models.generate_content(
                model=settings.gemini_model,
                contents=retry_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            ).text

            raw2 = (raw2 or "").strip()
            if not raw2:
                raise ValueError("Gemini returned empty response on retry (json)")

            try:
                return _safe_json_loads(raw2)
            except Exception as e2:
                dbg1 = raw[:1200]
                dbg2 = raw2[:1200]
                raise ValueError(
                    "Failed to parse Gemini JSON after retry. "
                    f"err1={type(e1).__name__}: {e1}; err2={type(e2).__name__}: {e2}; "
                    f"raw1={dbg1!r}; raw2={dbg2!r}"
                )

    except Exception as e:
        # quota exceeded -> chat.py дээр fallback хийхийн тулд алдааг дээш нь гаргана
        if _is_quota_error(e):
            raise
        raise


def llm_text(prompt: str) -> str:
    """
    Тайлбар/ярианд ашиглана.
    429 quota үед хоосон буцаана (chat.py base_answer руу fallback).
    """
    try:
        resp = _client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4),
        )
        return (resp.text or "").strip()

    except Exception as e:
        if _is_quota_error(e):
            return ""
        raise