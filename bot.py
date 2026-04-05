import json
import logging
import requests
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- AI Integration: Ollama llama3 for Risk Analysis ---
logger = logging.getLogger("bocorcheck.bot")
logging.basicConfig(level=logging.INFO)

def analyzeWithAI(osint_data: dict) -> dict | None:
    """
    FILDZA_AI_ACTIVE - Uses local Ollama (phi3) to generate dynamic mitigation plans.
    Lightweight model optimized for low-RAM systems.
    Returns dict with keys: risk_level, explanation, mitigation (immediate, short_term, long_term).
    Falls back to None on error, triggering static mitigation fallback.
    """
    url = "http://localhost:11434/api/generate"
    breaches = osint_data.get('breaches', [])
    data_types = sorted({d for b in breaches for d in b.get("DataClasses", [])})
    
    # Build structured breach summary for AI analysis
    breach_summary = ""
    for i, breach in enumerate(breaches, 1):
        breach_summary += f"\n  {i}. {breach.get('Name', 'Unknown')}: {', '.join(breach.get('DataClasses', []))} (Date: {breach.get('BreachDate', 'Unknown')})"
    
    # Determine primary risk factors
    has_password = any('Password' in b.get('DataClasses', []) for b in breaches)
    has_financial = any('FinancialData' in b.get('DataClasses', []) for b in breaches)
    has_phone = any('Phone' in b.get('DataClasses', []) for b in breaches)
    multiple_breaches = len(breaches) > 1
    
    # Optimized SHORT & DIRECT prompt for phi3 (lightweight model)
    # Use examples to enforce specific, non-generic responses
    prompt = f"""TASK: Analyze breach data and respond ONLY with JSON.
NO generic responses. Each action must reference the SPECIFIC exposed data.

BREACH DATA:
Email: {osint_data.get('email')}
Total Breaches: {len(breaches)}
Exposed Data Types: {', '.join(data_types) if data_types else 'Unknown'}{breach_summary}

RULES FOR ACTIONS (MUST FOLLOW):
1. If "Password" exposed → include password reset, 2FA, monitor logins
2. If "Email" exposed → include account recovery check, email security
3. If "FinancialData" exposed → include credit monitoring, fraud alert, bank contact
4. If "Phone" exposed → include SIM swap check, carrier contact
5. If {len(breaches)}+ breaches → ESCALATE risk to HIGH, add urgent actions
6. NEVER give generic advice like "use strong password" - be SPECIFIC to DATA TYPE

EXAMPLE OUTPUT (with specific actions):
{{"risk_level": "HIGH", "explanation": "Password and financial data breached. Immediate action required.", "mitigation": {{"immediate": ["Reset password on affected account immediately", "Enable 2FA/MFA on all financial accounts", "Contact your bank to report data breach"], "short_term": ["Monitor credit reports for fraud", "Place fraud alert with credit bureaus", "Update recovery email/phone in all accounts"], "long_term": ["Use unique password for each account", "Subscribe to credit monitoring", "Enable breach notifications"]}}}}

NOW ANALYZE THIS SPECIFIC CASE AND RESPOND ONLY WITH JSON:
{{"risk_level": "HIGH|MEDIUM|LOW", "explanation": "Specific analysis based on exposed data types", "mitigation": {{"immediate": ["specific action for {', '.join(data_types) if data_types else 'exposed data'} - be SPECIFIC"], "short_term": ["specific action"], "long_term": ["specific action"]}}}}""".strip()

    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"FILDZA_AI_ACTIVE - Ollama Analysis Started")
    logger.info(f"{'='*60}")
    logger.info(f"Email: {osint_data.get('email')}")
    logger.info(f"Breaches: {len(breaches)}")
    logger.info(f"Data types: {', '.join(data_types) if data_types else 'None'}")
    logger.info(f"Password exposed: {has_password} | Financial: {has_financial} | Phone: {has_phone} | Multiple: {multiple_breaches}")
    logger.info(f"Model: phi3 | Timeout: 40s")
    logger.info(f"\nBreach Details:")
    for i, breach in enumerate(breaches, 1):
        logger.info(f"  {i}. {breach.get('Name')}: {breach.get('DataClasses')}")
    logger.debug(f"\nFull Prompt:\n{prompt}")

    try:
        logger.info("Connecting to Ollama (http://localhost:11434/api/generate)...")
        response = requests.post(url, json=payload, timeout=40)
        
        if response.status_code != 200:
            logger.error(f"❌ Ollama returned {response.status_code}: {response.text}")
            logger.error("Fallback: Using static mitigation")
            return None
        
        logger.info(f"✓ Ollama responded (status {response.status_code})")
        data = response.json()
        response_text = data.get("response", "")
        logger.info(f"Response length: {len(response_text)} chars")
        
        # Extract JSON from response
        start = response_text.find("{")
        end = response_text.rfind("}")
        
        if start == -1 or end == -1:
            logger.error(f"❌ No JSON found in response")
            logger.error(f"Response: {response_text[:200]}")
            return None
        
        json_str = response_text[start:end+1]
        
        try:
            ai_result = json.loads(json_str)
            logger.info(f"✓ JSON parsed successfully")
            
            # Validate structure
            required_keys = {"risk_level", "explanation", "mitigation"}
            if not required_keys.issubset(ai_result.keys()):
                logger.error(f"❌ Missing keys: {required_keys - set(ai_result.keys())}")
                return None
            
            mitigation = ai_result.get("mitigation", {})
            if not all(k in mitigation for k in ["immediate", "short_term", "long_term"]):
                logger.error(f"❌ Mitigation missing required keys")
                return None
            
            logger.info(f"✓ FILDZA_AI_ACTIVE - Analysis Complete")
            logger.info(f"\n{'='*60}")
            logger.info(f"AI RESULT FOR: {osint_data.get('email')}")
            logger.info(f"{'='*60}")
            logger.info(f"Risk Level: {ai_result.get('risk_level')}")
            logger.info(f"Explanation: {ai_result.get('explanation')}")
            logger.info(f"Immediate Actions ({len(mitigation.get('immediate', []))}):")
            for action in mitigation.get('immediate', []):
                logger.info(f"  • {action}")
            logger.info(f"Short-term Actions ({len(mitigation.get('short_term', []))}):")
            for action in mitigation.get('short_term', []):
                logger.info(f"  • {action}")
            logger.info(f"Long-term Actions ({len(mitigation.get('long_term', []))}):")
            for action in mitigation.get('long_term', []):
                logger.info(f"  • {action}")
            logger.info(f"{'='*60}\n")
            
            return ai_result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse failed: {e}")
            logger.error(f"JSON: {json_str[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Cannot connect to Ollama at http://localhost:11434")
        logger.error(f"Run: ollama run phi3")
        logger.error(f"Fallback: Using static mitigation")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"❌ Ollama timeout (40s) - model too slow or not loaded")
        logger.error(f"Fallback: Using static mitigation")
        return None
    except Exception as e:
        logger.error(f"❌ AI error: {e}")
        return None

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
    If empty or "0", bot is open to any chat that can access it.
    """
    # Allow all if ALLOWED_CHAT_ID is not set, empty, or is "0"
    if not ALLOWED_CHAT_ID or ALLOWED_CHAT_ID == "0":
        return True
    # Debug: Log the chat ID trying to access
    logger.warning(f"🔐 Access attempt from chat ID: {chat_id} | Allowed: {ALLOWED_CHAT_ID}")
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

    # No breaches found
    if not breaches:
        logger.info(f"No breaches found for {email}")
        await update.message.reply_text(_build_no_breach_message(email))
        return

    # Prepare data for AI analysis
    logger.info(f"Found {len(breaches)} breach(es) for {email}")
    osint_data = {
        "email": email,
        "breaches": breaches,
    }

    # Try AI-powered analysis
    ai_result = None
    try:
        logger.info("FILDZA_AI_ACTIVE - Starting AI mitigation generation")
        ai_result = analyzeWithAI(osint_data)
    except Exception as e:
        logger.error(f"FILDZA_AI_ACTIVE - Exception during AI analysis: {e}", exc_info=True)
        ai_result = None

    # Format response
    if ai_result and "risk_level" in ai_result:
        # Use AI-generated mitigation
        logger.info("FILDZA_AI_ACTIVE - Using AI-generated mitigation plan")
        
        lines = [
            f"🔍 BREACH ANALYSIS FOR: {email}",
            f"{'='*50}",
            "",
        ]
        
        # List breaches
        for i, breach in enumerate(breaches, 1):
            lines.extend([
                f"Breach #{i}:",
                f"  Company: {breach.get('Name', 'Unknown')}",
                f"  Date: {breach.get('BreachDate', 'Unknown')}",
                f"  Data Exposed: {', '.join(breach.get('DataClasses', []))}",
                "",
            ])
        
        # AI Analysis
        risk_level = ai_result.get('risk_level', 'UNKNOWN').upper()
        risk_emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        
        lines.extend([
            f"{risk_emoji} AI RISK ASSESSMENT: {risk_level}",
            f"📋 Analysis: {ai_result.get('explanation', 'N/A')}",
            "",
            f"🛡️ AI-GENERATED MITIGATION PLAN",
            f"{'='*50}",
            "",
        ])
        
        # Immediate Actions
        immediate = ai_result.get('mitigation', {}).get('immediate', [])
        lines.append("⚠️ IMMEDIATE ACTIONS (Do NOW):")
        for idx, action in enumerate(immediate, 1):
            lines.append(f"  {idx}. {action}")
        lines.append("")
        
        # Short-term Actions
        short_term = ai_result.get('mitigation', {}).get('short_term', [])
        lines.append("📅 SHORT-TERM ACTIONS (Days 1-7):")
        for idx, action in enumerate(short_term, 1):
            lines.append(f"  {idx}. {action}")
        lines.append("")
        
        # Long-term Actions
        long_term = ai_result.get('mitigation', {}).get('long_term', [])
        lines.append("🔄 LONG-TERM ACTIONS (Ongoing):")
        for idx, action in enumerate(long_term, 1):
            lines.append(f"  {idx}. {action}")
        
        lines.append(f"\n{'='*50}")
        lines.append("Status: AI-Powered Recommendation (FILDZA_AI_ACTIVE)")
        
        message_text = "\n".join(lines)
        logger.info(f"FILDZA_AI_ACTIVE - Sending AI-powered response to Telegram")
        await update.message.reply_text(message_text)
    else:
        # Fallback to static mitigation
        logger.info("FILDZA_AI_ACTIVE - Fallback: Using static mitigation plan")
        await update.message.reply_text(_build_breach_message(email, breaches))


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
    logger.info(f"AI Model: phi3 (lightweight)")
    logger.info(f"Ollama Endpoint: http://localhost:11434/api/generate")
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
    application.run_polling()


if __name__ == "__main__":
    main()
