"""Demo chat endpoint exposed when ``ENABLE_TEST_CHAT=true``.

This lightweight router keeps the demo UI working without requiring
authentication or access to the full chat stack.  It provides a
structured response similar to the production endpoint but uses simple
heuristics so it can operate in isolation.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# FastAPI router intentionally unauthenticated so the static demo can call it
# without the usual auth headers.
test_router = APIRouter()


class TestChatRequest(BaseModel):
    """Request payload accepted by the demo chat endpoint."""

    message: str = Field(..., min_length=1, description="User message")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation identifier maintained by the demo UI.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Legacy field kept for backwards compatibility with the UI.",
    )
    persona: Optional[str] = Field(
        default="partner",
        description="Requested consultant persona (associate/partner/senior_partner).",
    )
    metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Optional metadata forwarded by the frontend for debugging.",
    )


class TestChatResponse(BaseModel):
    """Structured response returned to the demo UI."""

    message: str
    model_used: str
    complexity_score: float = Field(ge=0.0, le=1.0)
    routing_signals: List[str]
    conversation_id: str
    persona: str


def _estimate_complexity(message: str) -> float:
    """Very small heuristic for a pseudo complexity score."""

    words = [word for word in message.replace("\n", " ").split(" ") if word]
    if not words:
        return 0.2

    unique_ratio = len({word.strip(',.!?;:').lower() for word in words}) / len(words)
    length_score = min(1.0, len(words) / 120)  # Cap to keep the score within bounds
    score = 0.25 + (0.5 * length_score) + (0.25 * unique_ratio)
    return round(min(score, 1.0), 2)


def _summarise_prompt(message: str) -> str:
    """Create a short summary that feels conversational."""

    compact = " ".join(message.split())
    if len(compact) <= 120:
        return compact
    return f"{compact[:117]}..."


def _build_demo_message(summary: str, persona: str, complexity: float) -> str:
    """Format a friendly response for the static demo."""

    insight_level = "quick pulse"
    if complexity > 0.75:
        insight_level = "deep-dive framing"
    elif complexity > 0.5:
        insight_level = "structured assessment"

    return (
        "Thanks for trying the ValtricAI demo!\n\n"
        f"**Prompt focus:** {summary}\n\n"
        f"Persona **{persona.title()}** is responding with a {insight_level}.\n"
        "Here is how a production response would typically look:\n"
        "1. Highlight the business context and desired outcomes.\n"
        "2. Frame quick insights to guide an executive conversation.\n"
        "3. Suggest immediate next steps or deeper analysis modules.\n\n"
        "This endpoint runs in demo mode only—set `ENABLE_TEST_CHAT=false` to disable it."
    )


def _generate_routing_signals(persona: Optional[str], complexity: float, metadata: Dict[str, str]) -> List[str]:
    """Return simple routing metadata for the frontend console."""

    signals = ["demo-mode", f"persona:{(persona or 'partner').lower()}"]

    if complexity > 0.75:
        signals.append("strategic-depth")
    elif complexity > 0.5:
        signals.append("balanced-analysis")
    else:
        signals.append("quick-take")

    if metadata:
        signals.append("metadata-present")

    return signals


@test_router.post("/test-chat", response_model=TestChatResponse, summary="Demo chat endpoint")
async def test_chat_endpoint(request: TestChatRequest) -> TestChatResponse:
    """Return a deterministic, demo-friendly response for the static chat UI."""

    logger.info("Demo chat request received", extra={"persona": request.persona})

    complexity = _estimate_complexity(request.message)
    summary = _summarise_prompt(request.message)
    persona = request.persona or "partner"
    conversation_id = request.conversation_id or request.session_id or str(uuid4())

    response_message = _build_demo_message(summary, persona, complexity)
    routing_signals = _generate_routing_signals(persona, complexity, request.metadata or {})

    return TestChatResponse(
        message=response_message,
        model_used="demo-consultant-v1",
        complexity_score=complexity,
        routing_signals=routing_signals,
        conversation_id=conversation_id,
        persona=persona,
    )


__all__ = ["test_router"]
