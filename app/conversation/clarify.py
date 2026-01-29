from typing import Optional, Dict, Any
from .models import ConversationState


def needs_clarification(s: ConversationState) -> Optional[Dict[str, Any]]:
    """
    Зөвхөн үнэхээр ambiguity байвал л асууна
    """

    # ❌ metric clarify-г авна (backend өөрөө infer хийж чадна)

    # ⏱ time clarify — зөвхөн explicit огноо, latest байхгүй үед
    if not (s.time.year or s.time.years or getattr(s.time, "latest", False)):
        return {
            "question": "Аль оны мэдээлэл вэ?",
            "choices": [
                {"label": "2025 он", "prompt": "2025 он"},
                {"label": "2024 он", "prompt": "2024 он"},
                {"label": "Харьцуулах", "prompt": "2024, 2025 харьцуул"},
            ],
        }

    return None