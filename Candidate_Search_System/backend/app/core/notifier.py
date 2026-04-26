"""
notifier.py — fire-and-forget Slack / email delivery via N8N.

Runs as a background asyncio task so it never delays SSE stream.
"""

import logging
import httpx
from app.config import Config

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30)
    return _client


async def send_notification_background(request, candidates: list) -> None:
    """
    Forward search results to N8N for Slack / email delivery.

    🔥 HARD RULES:
    - Never send empty or invalid results
    - Never send if role/industry is missing
    - Never block main SSE flow
    """

    # ─────────────────────────────────────────────
    # 1. Safety guard — no webhook configured
    # ─────────────────────────────────────────────
    if not Config.N8N_WEBHOOK_URL:
        logger.debug("N8N_WEBHOOK_URL not configured — skipping notification")
        return

    # ─────────────────────────────────────────────
    # 2. Safety guard — empty results
    # ─────────────────────────────────────────────
    if not candidates:
        logger.info("Skipping N8N notification — empty candidates")
        return

    # ─────────────────────────────────────────────
    # 3. Extract request fields safely
    # ─────────────────────────────────────────────
    output_channel = getattr(request, "output_channel", None) or "slack"
    recipient_email = getattr(request, "recipient_email", None)
    industry = getattr(request, "industry", None)
    role_keywords = getattr(request, "role_keywords", None)

    # ─────────────────────────────────────────────
    # 4. STRICT VALIDATION (matches voice.py rules)
    # ─────────────────────────────────────────────

    if not industry:
        logger.warning("Skipping N8N — missing industry")
        return

    if not role_keywords:
        logger.warning("Skipping N8N — missing role_keywords")
        return

    if output_channel == "email" and not recipient_email:
        logger.warning(
            "output_channel='email' but no recipient_email provided — skipping notification"
        )
        return

    # ─────────────────────────────────────────────
    # 5. Build payload
    # ─────────────────────────────────────────────
    payload = {
        "query": getattr(request, "query", ""),
        "industry": industry,
        "role_keywords": role_keywords,
        "salary_range": getattr(request, "salary_range", None),
        "location_filter": getattr(request, "location_filter", None),
        "output_channel": output_channel,
        "recipient_email": recipient_email,
        "results": candidates,
    }

    # ─────────────────────────────────────────────
    # 6. Fire-and-forget request
    # ─────────────────────────────────────────────
    try:
        client = _get_client()

        resp = await client.post(
            Config.N8N_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        resp.raise_for_status()

        logger.info(
            "N8N notified successfully (channel=%s, results=%d)",
            output_channel,
            len(candidates),
        )

    except httpx.TimeoutException:
        logger.warning("N8N webhook timed out — notification not delivered")

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "N8N returned %s — %s",
            exc.response.status_code,
            exc.response.text[:200],
        )

    except Exception as exc:
        logger.error("Unexpected error notifying N8N: %s", exc)