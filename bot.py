import os
import re
from typing import List, Dict, Any

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app import (
    API_KEY,
    calculate_risk,
    get_mitigation_tips,
    is_mock_mode_enabled,
    query_hibp_breaches,
    query_mock_breaches,
)

# Put your BotFather token in environment variable TELEGRAM_BOT_TOKEN.
# Keep placeholder in code to avoid exposing secret in thesis repository.
BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8784573630:AAGHKXGUIdZLzVgE0L1aZkM1uzz0_r5o9Bk",
)

# Optional: restrict bot replies to a single Telegram chat/user ID.
# Example: TELEGRAM_CHAT_ID=5917103363
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5917103363")

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _is_chat_allowed(chat_id: int) -> bool:
    """
    Restrict access if TELEGRAM_CHAT_ID is configured.
    If empty, bot is open to any chat that can access it.
    """
    if not ALLOWED_CHAT_ID:
        return True
    return str(chat_id) == ALLOWED_CHAT_ID


def _build_no_breach_message(email: str) -> str:
    tips = get_mitigation_tips(risk_level="Low", has_breach=False)
    lines = [
        f"No known breach found for {email}.",
        "Status: Your data is safe.",
        "",
        "Mitigation Tips:",
    ]
    for idx, tip in enumerate(tips, start=1):
        lines.append(f"{idx}. {tip}")
    return "\n".join(lines)


def _build_breach_message(email: str, breaches: List[Dict[str, Any]]) -> str:
    """
    Convert breach records into Telegram-friendly text summary.
    """
    formatted_lines = [f"Breach incidents found for {email}:"]
    overall_risk = "Low"

    for breach in breaches:
        breach_name = breach.get("Name", "Unknown")
        breach_date = breach.get("BreachDate", "Unknown")
        data_classes = breach.get("DataClasses", [])
        current_risk = calculate_risk(data_classes)

        if current_risk == "High":
            overall_risk = "High"
        elif current_risk == "Medium" and overall_risk != "High":
            overall_risk = "Medium"

        formatted_lines.extend(
            [
                "",
                f"- Company: {breach_name}",
                f"  Date: {breach_date}",
                f"  Data: {', '.join(data_classes)}",
                f"  Risk: {current_risk}",
            ]
        )

    tips = get_mitigation_tips(risk_level=overall_risk, has_breach=True)
    formatted_lines.extend(["", f"Overall Risk: {overall_risk}", "", "Mitigation Tips:"])
    for idx, tip in enumerate(tips, start=1):
        formatted_lines.append(f"{idx}. {tip}")

    return "\n".join(formatted_lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Basic help command for user onboarding.
    """
    del context
    if update.effective_chat is None or not _is_chat_allowed(update.effective_chat.id):
        return

    await update.message.reply_text(
        "Welcome to OSINT Breach Bot.\n"
        "Use: /check your_email@example.com\n"
        "Example: /check fildza@ur.unirazak.edu.my"
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /check [email]
    Runs the same mock/live breach lookup logic used by the Flask dashboard.
    """
    if update.effective_chat is None or update.message is None:
        return

    if not _is_chat_allowed(update.effective_chat.id):
        await update.message.reply_text("This bot is restricted to an authorized chat ID.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /check your_email@example.com")
        return

    email = context.args[0].strip().lower()
    if not EMAIL_REGEX.match(email):
        await update.message.reply_text("Invalid email format. Please provide a valid email.")
        return

    if is_mock_mode_enabled():
        breaches = query_mock_breaches(email)
    else:
        try:
            breaches = query_hibp_breaches(email=email, api_key=API_KEY)
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response else "unknown"
            await update.message.reply_text(
                f"HIBP request failed with status {status_code}. Please try again later."
            )
            return
        except requests.RequestException:
            await update.message.reply_text("Network error while contacting HIBP API.")
            return

    if not breaches:
        await update.message.reply_text(_build_no_breach_message(email))
        return

    await update.message.reply_text(_build_breach_message(email, breaches))


def main() -> None:
    """
    Entry point for Telegram bot process.
    """
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        raise ValueError(
            "Telegram token missing. Set TELEGRAM_BOT_TOKEN environment variable."
        )

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check))

    # Polling mode is easiest for local prototype demonstration.
    application.run_polling()


if __name__ == "__main__":
    main()
