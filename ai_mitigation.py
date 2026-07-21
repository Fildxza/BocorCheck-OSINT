"""
AI Mitigation Module for BocorCheck
FILDZA_AI_ACTIVE - Centralized AI-powered mitigation engine using a local Ollama model.

This is the single AI mitigation engine used by BOTH the Flask web app (see the
/ai-proof route in app.py) and the Telegram bot (bot.py). Neither of those callers
should implement their own Ollama-calling or JSON-parsing logic - they call
generate_ai_mitigation() and render whatever it returns.

Responsibilities:
- Build a cybersecurity-consultant prompt from all available breach evidence
- Call the local Ollama instance with retries and bounded timeouts
- Robustly extract/validate the JSON response, tolerating minor omissions
- Always return a complete, uniformly-shaped result - falling back to a static,
  rule-based plan (tagged ai_powered=False) if Ollama is unreachable, slow, or
  returns something unusable
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("bocorcheck.ai_mitigation")
logging.basicConfig(level=logging.INFO)

# --- Configuration (env-overridable; names match the existing /ai-proof route) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434").rstrip("/")
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "1"))
OLLAMA_RETRY_BACKOFF_SECONDS = float(os.getenv("OLLAMA_RETRY_BACKOFF_SECONDS", "1.5"))

MITIGATION_CATEGORIES = ("immediate", "short_term", "long_term")
DEFAULT_PRIORITY = {
    "immediate": "Critical",
    "short_term": "High",
    "long_term": "Medium",
    "best_practices": "Low",
}


_PLACEHOLDER_PATTERN = re.compile(r"^(\.{2,}|etc\.?|n/a|tbd)$", re.IGNORECASE)


def _drop_placeholder_items(items: Any) -> List[str]:
    """
    Strip non-string entries and literal placeholder tokens (e.g. "...", "etc")
    that a small model occasionally echoes from the prompt's example shape
    instead of generating a real recommendation.
    """
    if not isinstance(items, list):
        return []
    return [item.strip() for item in items if isinstance(item, str) and item.strip() and not _PLACEHOLDER_PATTERN.match(item.strip())]


def _extract_first_json_object(text: str) -> Optional[str]:
    """
    Extract the first top-level JSON object from a model response, tolerating
    surrounding prose or markdown code fences (small models rarely respond with
    pure JSON only).
    """
    if not text:
        return None

    fence_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, flags=re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1].strip()

    return None


def _static_mitigation(
    risk_level: str,
    explanation: str,
    immediate: List[str],
    short_term: List[str],
    long_term: List[str],
    best_practices: List[str],
    ai_powered: bool,
) -> Dict[str, Any]:
    """Build a fully-shaped mitigation result (used for both the no-breach case and the AI-unavailable fallback)."""
    return {
        "risk_level": risk_level,
        "explanation": explanation,
        "mitigation": {
            "immediate": immediate,
            "short_term": short_term,
            "long_term": long_term,
        },
        "best_practices": best_practices,
        "priority": dict(DEFAULT_PRIORITY),
        "ai_powered": ai_powered,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _rule_based_fallback(
    breaches: List[Dict[str, Any]],
    risk_level: Optional[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
) -> Dict[str, Any]:
    """
    Static, rule-based mitigation plan used whenever Ollama is unavailable or
    returns something unusable. Tagged ai_powered=False so callers can label it.
    Uses the caller-supplied risk_level when available so the fallback stays
    consistent with the app's own risk-scoring, instead of a hardcoded guess.
    """
    level = (risk_level or ("HIGH" if len(breaches) >= 3 else "MEDIUM")).upper()

    immediate = [
        "Change your password on the affected account(s) immediately",
        "Enable two-factor authentication (2FA) wherever it is offered",
    ]
    short_term = [
        "Review recent account activity and active sessions for anything unfamiliar",
        "Update recovery email/phone details on affected accounts",
    ]
    long_term = [
        "Use a unique password per account, ideally via a password manager",
        "Subscribe to breach-notification alerts for your email",
    ]
    best_practices = [
        "Never reuse passwords across services",
        "Treat unexpected password-reset or login emails as suspicious until verified",
    ]

    if has_password:
        immediate.insert(0, "Reset the password immediately - it was exposed in a known breach")
    if has_financial:
        immediate.append("Contact your bank to flag the account and monitor for fraud")
        short_term.append("Place a fraud alert with your bank/credit provider")
    if has_phone:
        short_term.append("Contact your mobile carrier to check for unauthorized SIM-swap requests")

    explanation = (
        f"Automated rule-based assessment: {len(breaches)} breach(es) detected. "
        "This is a static fallback plan because the AI mitigation service was unavailable."
    )
    return _static_mitigation(level, explanation, immediate, short_term, long_term, best_practices, ai_powered=False)


def _build_prompt(
    email: str,
    breaches: List[Dict[str, Any]],
    data_types: List[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    phone_number: Optional[str],
    phone_exposed: bool,
    risk_score: Optional[int],
    risk_level: Optional[str],
) -> str:
    """Build a production prompt framing the model as a cybersecurity incident-response consultant."""
    breach_lines = "\n".join(
        f"  {i}. {b.get('Name', 'Unknown')} ({b.get('BreachDate', 'unknown date')}): "
        f"{', '.join(b.get('DataClasses', [])) or 'unspecified data'}"
        for i, b in enumerate(breaches, 1)
    ) or "  (none)"

    evidence_lines = [
        f"- Email under investigation: {email}",
        f"- Total breaches found: {len(breaches)}",
        f"- Exposed data categories: {', '.join(data_types) if data_types else 'unknown'}",
        f"- Password exposed: {'YES' if has_password else 'no'}",
        f"- Financial data exposed: {'YES' if has_financial else 'no'}",
        f"- Phone number exposed: {'YES' if (has_phone or phone_exposed) else 'no'}"
        + (f" ({phone_number})" if phone_number and (has_phone or phone_exposed) else ""),
    ]
    if risk_score is not None:
        evidence_lines.append(f"- Computed risk score: {risk_score}/100")
    if risk_level:
        evidence_lines.append(f"- Computed risk tier: {risk_level}")

    return f"""You are a professional cybersecurity consultant and incident response advisor. \
A client's personal data has appeared in one or more data breaches. Analyze the evidence below \
and produce a remediation plan a non-technical person can follow.

EVIDENCE:
{chr(10).join(evidence_lines)}

BREACH HISTORY:
{breach_lines}

INSTRUCTIONS:
- Every action must be specific to the evidence above (which data types are exposed, how many \
breaches, whether financial/phone data is involved) - never give generic advice like "use a strong password".
- If a password was exposed, prioritize credential rotation and 2FA.
- If financial data was exposed, prioritize fraud alerts and bank contact.
- If a phone number was exposed, prioritize SIM-swap and carrier checks.
- More breaches or more sensitive data types should escalate the risk_level.
- Each list must contain 2 to 4 concrete items written out in full. Never include placeholder \
text such as "..." or "etc" - every array entry must be a complete, real recommendation.
- Respond with ONLY a single JSON object, no prose before or after, matching exactly this shape \
(the example text below is illustrative only - replace it with your own analysis):

{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "explanation": "1-2 concise sentences grounded in the evidence above",
  "mitigation": {{
    "immediate": ["first concrete action to take right now", "second concrete action"],
    "short_term": ["first concrete action for the next 1-7 days", "second concrete action"],
    "long_term": ["first concrete ongoing security habit", "second concrete habit"]
  }},
  "best_practices": ["first general best practice relevant to this case", "second best practice"],
  "priority": {{
    "immediate": "Critical|High|Medium|Low",
    "short_term": "Critical|High|Medium|Low",
    "long_term": "Critical|High|Medium|Low",
    "best_practices": "Critical|High|Medium|Low"
  }}
}}"""


def _validate_and_normalize(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate the model's JSON has the required core keys, and backfill optional
    ones (best_practices/priority) if the model omitted them - a small model
    getting the core fields right but skipping an extra key shouldn't force a
    full fallback.
    """
    if not isinstance(result, dict):
        return None
    if not {"risk_level", "explanation", "mitigation"}.issubset(result.keys()):
        return None

    mitigation = result.get("mitigation")
    if not isinstance(mitigation, dict) or not all(k in mitigation for k in MITIGATION_CATEGORIES):
        return None

    for key in MITIGATION_CATEGORIES:
        mitigation[key] = _drop_placeholder_items(mitigation.get(key))
        if not mitigation[key]:
            return None  # a core category with only placeholder junk isn't a usable plan

    result["best_practices"] = _drop_placeholder_items(result.get("best_practices")) or [
        "Use a password manager and enable 2FA on all important accounts"
    ]
    result.setdefault("priority", dict(DEFAULT_PRIORITY))
    for key, value in DEFAULT_PRIORITY.items():
        result["priority"].setdefault(key, value)

    result["risk_level"] = str(result.get("risk_level", "MEDIUM")).upper()
    result["ai_powered"] = True
    result["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result


def _call_ollama_once(prompt: str) -> Optional[Dict[str, Any]]:
    """Single Ollama request attempt. Returns a validated dict, or None if this attempt failed."""
    # format="json" makes Ollama constrain decoding to valid JSON - small models like
    # phi3 otherwise occasionally emit unescaped quotes/newlines inside string values
    # that break json.loads() even when the overall shape looks right.
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"}
    response = requests.post(OLLAMA_GENERATE_URL, json=payload, timeout=OLLAMA_TIMEOUT_SECONDS)

    if response.status_code != 200:
        logger.warning(f"Ollama returned HTTP {response.status_code}: {response.text[:300]}")
        return None

    data = response.json()
    response_text = data.get("response") or data.get("message", {}).get("content") or data.get("content") or ""
    json_str = _extract_first_json_object(response_text)
    if not json_str:
        logger.warning(f"No JSON object found in Ollama response: {response_text[:200]}")
        return None

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.warning(f"JSON parse failed: {exc} | raw: {json_str[:200]}")
        return None

    return _validate_and_normalize(parsed)


def generate_ai_mitigation(
    email: str,
    breaches: List[Dict[str, Any]],
    phone_number: Optional[str] = None,
    phone_exposed: bool = False,
    risk_score: Optional[int] = None,
    risk_level: Optional[str] = None,
) -> Dict[str, Any]:
    """
    FILDZA_AI_ACTIVE - Generate a mitigation plan for the given breach evidence.

    Always returns a fully-shaped dict (never None): risk_level, explanation,
    mitigation.{immediate,short_term,long_term}, best_practices, priority,
    ai_powered. Falls back to a static rule-based plan (ai_powered=False) if
    Ollama is unreachable, slow, or its response can't be parsed after retries.
    """
    logger.info(f"AI mitigation requested for {email} ({len(breaches)} breach(es))")

    if not breaches:
        return _static_mitigation(
            risk_level="LOW",
            explanation="No known data breaches found for this email.",
            immediate=["No immediate action required"],
            short_term=["Continue monitoring for new breaches"],
            long_term=["Maintain strong, unique passwords across accounts"],
            best_practices=["Enable breach-notification alerts for this email"],
            ai_powered=False,
        )

    data_types = sorted({d for b in breaches for d in b.get("DataClasses", [])})
    has_password = any("password" in d.lower() for d in data_types)
    has_financial = any(
        d.lower() in ("financial information", "financialdata", "credit cards", "payment history")
        for d in data_types
    )
    has_phone = any("phone" in d.lower() for d in data_types)

    prompt = _build_prompt(
        email=email,
        breaches=breaches,
        data_types=data_types,
        has_password=has_password,
        has_financial=has_financial,
        has_phone=has_phone,
        phone_number=phone_number,
        phone_exposed=phone_exposed,
        risk_score=risk_score,
        risk_level=risk_level,
    )

    attempts = OLLAMA_MAX_RETRIES + 1
    last_error: Optional[str] = None
    for attempt in range(1, attempts + 1):
        try:
            logger.info(f"Ollama attempt {attempt}/{attempts} (model={OLLAMA_MODEL}, timeout={OLLAMA_TIMEOUT_SECONDS}s)")
            result = _call_ollama_once(prompt)
            if result is not None:
                logger.info(f"AI mitigation succeeded on attempt {attempt}: risk_level={result.get('risk_level')}")
                return result
            last_error = "Ollama response was unusable (bad status, no JSON, or failed validation)"
        except requests.exceptions.ConnectionError as exc:
            last_error = f"Cannot connect to Ollama at {OLLAMA_BASE_URL}: {exc}"
        except requests.exceptions.Timeout as exc:
            last_error = f"Ollama timed out after {OLLAMA_TIMEOUT_SECONDS}s: {exc}"
        except Exception as exc:  # noqa: BLE001 - any unexpected failure must still fall back gracefully
            last_error = f"Unexpected error calling Ollama: {exc}"

        logger.warning(f"Attempt {attempt}/{attempts} failed: {last_error}")
        if attempt < attempts:
            time.sleep(OLLAMA_RETRY_BACKOFF_SECONDS * attempt)

    logger.error(f"AI mitigation exhausted all retries; using rule-based fallback. Last error: {last_error}")
    return _rule_based_fallback(breaches, risk_level, has_password, has_financial, has_phone)


def format_mitigation_for_display(mitigation: Dict[str, Any]) -> Dict[str, Any]:
    """Format a generate_ai_mitigation() result for HTML template display."""
    risk_level = mitigation.get("risk_level", "MEDIUM")
    return {
        "risk_level": risk_level,
        "risk_color": {"HIGH": "danger", "MEDIUM": "warning", "LOW": "success"}.get(risk_level, "info"),
        "explanation": mitigation.get("explanation", ""),
        "immediate": mitigation.get("mitigation", {}).get("immediate", []),
        "short_term": mitigation.get("mitigation", {}).get("short_term", []),
        "long_term": mitigation.get("mitigation", {}).get("long_term", []),
        "best_practices": mitigation.get("best_practices", []),
        "priority": mitigation.get("priority", dict(DEFAULT_PRIORITY)),
        "generated_at": mitigation.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "ai_powered": mitigation.get("ai_powered", False),
    }


def get_risk_emoji(risk_level: str) -> str:
    """Get emoji for risk level."""
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk_level, "⚪")


if __name__ == "__main__":
    test_breaches = [
        {"Name": "TestBreach", "BreachDate": "2024-01-01", "DataClasses": ["Email addresses", "Passwords"]},
    ]
    result = generate_ai_mitigation("test@example.com", test_breaches, risk_score=55, risk_level="MEDIUM")
    print(json.dumps(result, indent=2))
