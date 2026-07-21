import asyncio
import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ai_mitigation import OLLAMA_GENERATE_URL, OLLAMA_MODEL, generate_ai_mitigation
from app import (
    API_KEY,
    is_mock_mode_enabled,
    query_hibp_breaches,
    query_mock_breaches,
)

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("bocorcheck.bot")
logging.basicConfig(level=logging.INFO)


def analyzeWithAI(osint_data: dict) -> Optional[dict]:
    """
    FILDZA_AI_ACTIVE - Backward-compat shim for tooling that still imports
    analyzeWithAI from bot.py (e.g. debug_ai_mitigation.py). All actual AI
    logic now lives in ai_mitigation.generate_ai_mitigation - this module no
    longer has its own copy of the Ollama-calling / JSON-parsing code.
    """
    return generate_ai_mitigation(
        email=osint_data.get("email", ""),
        breaches=osint_data.get("breaches", []),
    )

# Put your BotFather token in environment variable TELEGRAM_BOT_TOKEN.
# Keep placeholder in code to avoid exposing secret in thesis repository.
BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8784573630:AAGrnWSCglPhDd4WHv_w-eNRNDLop-rDTs4",
)

# Optional: restrict bot replies to a single Telegram chat/user ID.
# Example: TELEGRAM_CHAT_ID=5917103363
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5917103363")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _is_chat_allowed(chat_id: int) -> bool:
    """
    Restrict access if TELEGRAM_CHAT_ID is configured.
    If empty or "0", bot is open to any chat that can access it.
    """
    # Allow all if ALLOWED_CHAT_ID is not set, empty, or is "0"
    if not ALLOWED_CHAT_ID or ALLOWED_CHAT_ID == "0":
        return True
    # Debug: Log the chat ID trying to access
    logger.warning(f"🔐 Access attempt from chat ID: {chat_id} | Allowed: {ALLOWED_CHAT_ID}")
    return str(chat_id) == ALLOWED_CHAT_ID


def _format_breach_list(breaches: List[Dict[str, Any]]) -> List[str]:
    """Render the per-breach company/date/data listing shared by both AI and fallback replies."""
    lines: List[str] = []
    for i, breach in enumerate(breaches, 1):
        lines.extend(
            [
                f"Breach #{i}:",
                f"  Company: {breach.get('Name', 'Unknown')}",
                f"  Date: {breach.get('BreachDate', 'Unknown')}",
                f"  Data Exposed: {', '.join(breach.get('DataClasses', []))}",
                "",
            ]
        )
    return lines


def _format_mitigation_message(email: str, breaches: List[Dict[str, Any]], mitigation: Dict[str, Any]) -> str:
    """
    Render a Telegram message from a generate_ai_mitigation() result. Works
    identically whether the result came from Ollama or the rule-based
    fallback - both have the exact same shape, so there is only one formatter.
    """
    if not breaches:
        lines = [f"No known breach found for {email}.", "Status: Your data is safe.", ""]
    else:
        risk_level = mitigation.get("risk_level", "UNKNOWN").upper()
        risk_emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"

        lines = [f"🔍 BREACH ANALYSIS FOR: {email}", "=" * 50, ""]
        lines.extend(_format_breach_list(breaches))
        lines.extend(
            [
                f"{risk_emoji} RISK ASSESSMENT: {risk_level}",
                f"📋 Analysis: {mitigation.get('explanation', 'N/A')}",
                "",
                "🛡️ MITIGATION PLAN",
                "=" * 50,
                "",
            ]
        )

    plan = mitigation.get("mitigation", {})
    priority = mitigation.get("priority", {})

    section_titles = {
        "immediate": "⚠️ IMMEDIATE ACTIONS (Do NOW)",
        "short_term": "📅 SHORT-TERM ACTIONS (Days 1-7)",
        "long_term": "🔄 LONG-TERM ACTIONS (Ongoing)",
    }
    for key, title in section_titles.items():
        actions = plan.get(key, [])
        if not actions:
            continue
        priority_label = priority.get(key)
        lines.append(f"{title}" + (f" [Priority: {priority_label}]" if priority_label else "") + ":")
        for idx, action in enumerate(actions, 1):
            lines.append(f"  {idx}. {action}")
        lines.append("")

    best_practices = mitigation.get("best_practices", [])
    if best_practices:
        bp_priority = priority.get("best_practices")
        lines.append("✅ BEST PRACTICES" + (f" [Priority: {bp_priority}]" if bp_priority else "") + ":")
        for idx, practice in enumerate(best_practices, 1):
            lines.append(f"  {idx}. {practice}")
        lines.append("")

    lines.append("=" * 50)
    if mitigation.get("ai_powered"):
        lines.append("Status: AI-Powered Recommendation (FILDZA_AI_ACTIVE)")
    else:
        lines.append("Status: Rule-Based Fallback (AI service unavailable)")

    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Basic help command for user onboarding.
    """
    del context
    if update.effective_chat is None:
        return

    # TODO: Uncomment below to enable chat ID restriction after setup
    # if not _is_chat_allowed(update.effective_chat.id):
    #     return

    await update.message.reply_text(
        "Welcome to OSINT Breach Bot.\n"
        "Use: /check your_email@example.com\n"
        "Example: /check fildza@ur.unirazak.edu.my"
    )
    logger.info(f"/start called by chat_id={update.effective_chat.id if update.effective_chat else 'N/A'}")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /check [email]
    FILDZA_AI_ACTIVE - Retrieves breach data and generates AI-powered mitigation recommendations.
    Falls back to static recommendations if AI unavailable.
    """
    if update.effective_chat is None or update.message is None:
        return

    # Log your chat ID for setup
    chat_id = update.effective_chat.id
    if str(chat_id) != ALLOWED_CHAT_ID:
        logger.info(f"✅ DEBUG: Your Telegram Chat ID is: {chat_id} | Current setting: {ALLOWED_CHAT_ID}")

    # TODO: Uncomment below to enable chat ID restriction after setup
    # if not _is_chat_allowed(update.effective_chat.id):
    #     await update.message.reply_text("This bot is restricted to an authorized chat ID.")
    #     return

    if not context.args:
        await update.message.reply_text("Usage: /check your_email@example.com")
        return

    email = context.args[0].strip().lower()
    if not EMAIL_REGEX.match(email):
        await update.message.reply_text("Invalid email format. Please provide a valid email.")
        return

    logger.info(f"\n{'='*60}")
    logger.info(f"FILDZA_AI_ACTIVE - /check command for: {email}")
    logger.info(f"{'='*60}")

    # Query breaches
    if is_mock_mode_enabled():
        breaches = query_mock_breaches(email)
        logger.info("Using mock breach data")
    else:
        try:
            breaches = query_hibp_breaches(email=email, api_key=API_KEY)
            logger.info(f"HIBP query returned {len(breaches) if breaches else 0} breaches")
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else "unknown"
            logger.error(f"HIBP error: {status_code}")
            await update.message.reply_text(
                f"HIBP request failed with status {status_code}. Please try again later."
            )
            return
        except requests.RequestException:
            logger.error("Network error contacting HIBP")
            await update.message.reply_text("Network error while contacting HIBP API.")
            return

    logger.info(f"Found {len(breaches)} breach(es) for {email}" if breaches else f"No breaches found for {email}")

    # FILDZA_AI_ACTIVE - centralized engine call, offloaded to a worker thread so
    # the bot's event loop stays responsive to other chats/commands while Ollama
    # (which can take up to OLLAMA_TIMEOUT_SECONDS x retries) is in flight.
    try:
        mitigation = await asyncio.to_thread(generate_ai_mitigation, email, breaches)
    except Exception as exc:
        logger.error(f"Unexpected error generating mitigation for {email}: {exc}", exc_info=True)
        await update.message.reply_text(
            "Something went wrong generating your mitigation plan. Please try again in a moment."
        )
        return

    message_text = _format_mitigation_message(email, breaches, mitigation)
    logger.info(
        f"Sending {'AI-powered' if mitigation.get('ai_powered') else 'rule-based fallback'} "
        f"response to Telegram for {email}"
    )
    await update.message.reply_text(message_text)


def main() -> None:
    """
    Entry point for Telegram bot process.
    FILDZA_AI_ACTIVE - Initializes bot with AI-powered mitigation support.
    """
    if not BOT_TOKEN or BOT_TOKEN.startswith("your_") or BOT_TOKEN == "PLACEHOLDER":
        raise ValueError(
            "Telegram token missing. Set TELEGRAM_BOT_TOKEN environment variable."
        )

    logger.info(f"\n{'='*60}")
    logger.info("🤖 FILDZA_AI_ACTIVE - BocorCheck Telegram Bot Starting")
    logger.info(f"{'='*60}")
    logger.info(f"AI Model: {OLLAMA_MODEL} (lightweight)")
    logger.info(f"Ollama Endpoint: {OLLAMA_GENERATE_URL}")
    logger.info(f"Chat ID Restriction: {ALLOWED_CHAT_ID if ALLOWED_CHAT_ID else 'NONE (Open)'}")
    logger.info(f"Mock Mode: {is_mock_mode_enabled()}")
    logger.info(f"\nFeatures:")
    logger.info(f"  ✓ /start - Help and usage")
    logger.info(f"  ✓ /check [email] - Breach check with AI mitigation")
    logger.info(f"  ✓ Fallback to static mitigation if AI unavailable")
    logger.info(f"{'='*60}\n")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))

    logger.info("✓ Handlers registered. Starting polling mode...")

    # python-telegram-bot's run_polling() calls the legacy asyncio.get_event_loop(),
    # which Python 3.10+ no longer auto-creates in the main thread if none is
    # running yet (and 3.12+/3.14 raise instead of silently creating one).
    # Restoring an explicit loop here keeps run_polling() working as it expects.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling()



if __name__ == "__main__":
    main()

