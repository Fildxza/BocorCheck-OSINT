"""
AI Mitigation Module for BocorCheck
FILDZA_AI_ACTIVE - Centralized AI cybersecurity-consultant engine using a local Ollama model.

This is the single AI mitigation engine used by BOTH the Flask web app (see the
/ai-proof and /ai-mitigation/* routes in app.py) and the Telegram bot (bot.py).
Neither of those callers should implement their own Ollama-calling or JSON-parsing
logic - they call generate_ai_mitigation() and render whatever it returns.

Responsibilities:
- Build a cybersecurity-consultant prompt from all available breach evidence
- Call the local Ollama instance with retries and bounded timeouts
- Robustly extract/validate the JSON response, tolerating minor omissions
- Deterministically map each detected exposure to its risk and related actions
  (the "explainable AI" evidence map - never left to the LLM to self-report)
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
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "1"))
OLLAMA_RETRY_BACKOFF_SECONDS = float(os.getenv("OLLAMA_RETRY_BACKOFF_SECONDS", "1.5"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))

MITIGATION_CATEGORIES = ("immediate", "short_term", "long_term")
DEFAULT_PRIORITY = {
    "immediate": "Critical",
    "short_term": "High",
    "long_term": "Medium",
    "best_practices": "Low",
}

# Consultant-report keys the AI is asked to generate, each with a safe fallback
# used when Ollama is unavailable or omits the key. Kept short/bounded in the
# prompt to control generation time and reduce truncation risk on a small model.
REPORT_TEXT_DEFAULTS = {
    "executive_summary": "Your personal data was found in one or more data breaches. Review the risk level and act on the recommendations below, starting with the immediate actions.",
    "threat_analysis": "The exposed data can be used by attackers for credential-stuffing, phishing, or identity fraud, with severity depending on how sensitive the leaked fields are and how many breaches are involved.",
    "business_impact": "Depending on account reuse, this exposure could lead to unauthorized account access, financial loss, or identity theft affecting your personal or professional accounts.",
    "attack_scenario": "An attacker could take the leaked credentials and attempt to log into other services where the same email/password combination is reused, or use exposed personal details to craft a convincing phishing message.",
    "overall_assessment": "Follow the immediate actions first, then the short-term and long-term steps, to substantially reduce the risk this exposure poses.",
}

# Deterministic evidence -> risk -> related-action-category catalog. This is the
# "explainable AI" layer: never AI-generated, so it is always accurate and never
# subject to small-model JSON reliability issues.
EVIDENCE_RISK_CATALOG = {
    "password": {
        "exposure": "Password",
        "risk": "Account takeover - attackers can log in directly using the leaked credentials, especially if the same password is reused elsewhere.",
        "action_categories": ["immediate"],
    },
    "financial": {
        "exposure": "Financial Information",
        "risk": "Financial fraud - exposed payment or account details can be used for unauthorized transactions or identity-based fraud.",
        "action_categories": ["immediate", "short_term"],
    },
    "phone": {
        "exposure": "Phone Number",
        "risk": "SIM-swap and phishing - a leaked phone number enables SIM-swap attacks and targeted smishing/vishing.",
        "action_categories": ["short_term"],
    },
}
EVIDENCE_RISK_CATALOG_FALLBACK = {
    "exposure": "Other exposed data",
    "risk": "General identity exposure - additional exposed fields (e.g. name, address, date of birth) widen the surface for identity-theft or social-engineering attacks.",
    "action_categories": ["best_practices"],
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


def build_evidence_map(
    data_types: List[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    mitigation: Dict[str, List[str]],
    best_practices: List[str],
) -> List[Dict[str, Any]]:
    """
    Deterministically pair each detected exposure with a fixed risk description
    and the actual related actions from the (AI-generated or fallback) plan.
    This is the "explainable AI" feature - kept rule-based rather than asking
    the LLM to self-report its own reasoning graph, since a 3.8B model already
    struggles with a flatter schema; a rule-derived mapping is instant, always
    correct, and grounded in the real generated action text.
    """
    action_pools = {**mitigation, "best_practices": best_practices}
    evidence_map: List[Dict[str, Any]] = []

    flags = [
        ("password", has_password),
        ("financial", has_financial),
        ("phone", has_phone),
    ]
    for key, present in flags:
        if not present:
            continue
        entry = EVIDENCE_RISK_CATALOG[key]
        related_actions: List[str] = []
        for category in entry["action_categories"]:
            related_actions.extend(action_pools.get(category, [])[:2])
        evidence_map.append(
            {
                "exposure": entry["exposure"],
                "risk": entry["risk"],
                "related_actions": related_actions,
            }
        )

    other_types = [d for d in data_types if not any(k in d.lower() for k in ("password", "financial", "credit card", "payment", "phone"))]
    if other_types:
        entry = EVIDENCE_RISK_CATALOG_FALLBACK
        evidence_map.append(
            {
                "exposure": f"Other data: {', '.join(other_types[:4])}",
                "risk": entry["risk"],
                "related_actions": action_pools.get("best_practices", [])[:2],
            }
        )

    return evidence_map


def _default_risk_reduction_narrative(risk_reduction: Dict[str, Any]) -> str:
    factors = risk_reduction.get("factors", [])
    if not factors:
        return "Following the immediate and short-term actions above addresses the reducible risk factors identified for this case."
    parts = [f"{f['factor']} (-{f['points']} pts) via {f['neutralized_by']}" for f in factors]
    return "Completing the recommended actions neutralizes: " + "; ".join(parts) + "."


def _full_report_shape(
    risk_level: str,
    explanation: str,
    immediate: List[str],
    short_term: List[str],
    long_term: List[str],
    best_practices: List[str],
    ai_powered: bool,
    data_types: List[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    risk_reduction: Optional[Dict[str, Any]],
    report_texts: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Build a fully-shaped report dict - the single contract shared by the AI path and every fallback path."""
    mitigation = {"immediate": immediate, "short_term": short_term, "long_term": long_term}
    texts = dict(REPORT_TEXT_DEFAULTS)
    if report_texts:
        # Only merge known report-section keys into the top level - risk_reduction_narrative
        # is intentionally excluded here since it belongs solely under risk_reduction.narrative below.
        texts.update({k: v for k, v in report_texts.items() if v and k in REPORT_TEXT_DEFAULTS})

    result: Dict[str, Any] = {
        "risk_level": risk_level,
        "explanation": explanation,
        "mitigation": mitigation,
        "best_practices": best_practices,
        "priority": dict(DEFAULT_PRIORITY),
        "ai_powered": ai_powered,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_map": build_evidence_map(data_types, has_password, has_financial, has_phone, mitigation, best_practices),
        **texts,
    }

    if risk_reduction is not None:
        result["risk_reduction"] = {
            **risk_reduction,
            "narrative": (report_texts or {}).get("risk_reduction_narrative") or _default_risk_reduction_narrative(risk_reduction),
        }
    return result


def _rule_based_fallback(
    breaches: List[Dict[str, Any]],
    risk_level: Optional[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    data_types: List[str],
    risk_reduction: Optional[Dict[str, Any]],
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
    return _full_report_shape(
        risk_level=level,
        explanation=explanation,
        immediate=immediate,
        short_term=short_term,
        long_term=long_term,
        best_practices=best_practices,
        ai_powered=False,
        data_types=data_types,
        has_password=has_password,
        has_financial=has_financial,
        has_phone=has_phone,
        risk_reduction=risk_reduction,
    )


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

    return f"""You are a professional cybersecurity consultant and incident response advisor writing \
a client-facing report. A client's personal data has appeared in one or more data breaches. Analyze \
the evidence below and produce a consultant-grade report a non-technical person can follow.

EVIDENCE:
{chr(10).join(evidence_lines)}

BREACH HISTORY:
{breach_lines}

INSTRUCTIONS:
- Every action and analysis must be specific to the evidence above - never give generic advice like \
"use a strong password".
- If a password was exposed, prioritize credential rotation and 2FA.
- If financial data was exposed, prioritize fraud alerts and bank contact.
- If a phone number was exposed, prioritize SIM-swap and carrier checks.
- More breaches or more sensitive data types should escalate the risk_level.
- Each mitigation list must contain 2 to 4 concrete items written out in full. Never include \
placeholder text such as "..." or "etc".
- Keep every prose field SHORT and within its stated sentence limit - this keeps the report readable \
and prevents truncation.
- Respond with ONLY a single JSON object, no prose before or after, matching exactly this shape \
(the example text below is illustrative only - replace it with your own analysis):

{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "explanation": "1-2 concise sentences grounded in the evidence above",
  "executive_summary": "2-3 sentences summarizing the case for a non-technical reader",
  "threat_analysis": "3-4 sentences analyzing the specific threat landscape for this exposure",
  "business_impact": "2-3 sentences on personal/business impact if exploited",
  "attack_scenario": "3-5 sentences describing one realistic attack chain an adversary could execute with this exposed data",
  "overall_assessment": "2-3 concluding sentences with a recommended security posture",
  "risk_reduction_narrative": "1-2 sentences on how following the immediate and short-term actions reduces risk",
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


def _validate_and_normalize(
    result: Dict[str, Any],
    data_types: List[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    risk_reduction: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Validate the model's JSON has the required core keys, and backfill optional
    ones (best_practices/priority/report sections) if the model omitted them -
    a small model getting the core fields right but skipping an extra key
    shouldn't force a full fallback.
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

    best_practices = _drop_placeholder_items(result.get("best_practices")) or [
        "Use a password manager and enable 2FA on all important accounts"
    ]

    priority = result.get("priority") if isinstance(result.get("priority"), dict) else {}
    for key, value in DEFAULT_PRIORITY.items():
        priority.setdefault(key, value)

    report_texts = {key: result.get(key) for key in list(REPORT_TEXT_DEFAULTS) + ["risk_reduction_narrative"]}

    normalized = _full_report_shape(
        risk_level=str(result.get("risk_level", "MEDIUM")).upper(),
        explanation=result.get("explanation", ""),
        immediate=mitigation["immediate"],
        short_term=mitigation["short_term"],
        long_term=mitigation["long_term"],
        best_practices=best_practices,
        ai_powered=True,
        data_types=data_types,
        has_password=has_password,
        has_financial=has_financial,
        has_phone=has_phone,
        risk_reduction=risk_reduction,
        report_texts=report_texts,
    )
    normalized["priority"] = priority
    return normalized


def _call_ollama_once(
    prompt: str,
    data_types: List[str],
    has_password: bool,
    has_financial: bool,
    has_phone: bool,
    risk_reduction: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Single Ollama request attempt. Returns a validated dict, or None if this attempt failed."""
    # format="json" makes Ollama constrain decoding to valid JSON - small models like
    # phi3 otherwise occasionally emit unescaped quotes/newlines inside string values
    # that break json.loads() even when the overall shape looks right.
    # num_predict raises the generation token budget so the larger consultant-report
    # schema doesn't get truncated mid-JSON before it can close its braces.
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"num_predict": OLLAMA_NUM_PREDICT},
    }
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

    return _validate_and_normalize(parsed, data_types, has_password, has_financial, has_phone, risk_reduction)


def generate_ai_mitigation(
    email: str,
    breaches: List[Dict[str, Any]],
    phone_number: Optional[str] = None,
    phone_exposed: bool = False,
    risk_score: Optional[int] = None,
    risk_level: Optional[str] = None,
    risk_reduction: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    FILDZA_AI_ACTIVE - Generate a full cybersecurity-consultant report for the
    given breach evidence.

    Always returns a fully-shaped dict (never None): risk_level, explanation,
    mitigation.{immediate,short_term,long_term}, best_practices, priority,
    ai_powered, evidence_map, executive_summary, threat_analysis,
    business_impact, attack_scenario, overall_assessment, and - when the caller
    supplies risk_reduction (see app.py's estimate_risk_reduction()) - a
    risk_reduction section with an AI/fallback narrative attached. Falls back
    to a static rule-based plan (ai_powered=False) if Ollama is unreachable,
    slow, or its response can't be parsed after retries.
    """
    logger.info(f"AI mitigation requested for {email} ({len(breaches)} breach(es))")

    if not breaches:
        return _full_report_shape(
            risk_level="LOW",
            explanation="No known data breaches found for this email.",
            immediate=["No immediate action required"],
            short_term=["Continue monitoring for new breaches"],
            long_term=["Maintain strong, unique passwords across accounts"],
            best_practices=["Enable breach-notification alerts for this email"],
            ai_powered=False,
            data_types=[],
            has_password=False,
            has_financial=False,
            has_phone=False,
            risk_reduction=risk_reduction,
            report_texts={
                "executive_summary": "No known data breaches were found for this email. No action is required at this time.",
                "threat_analysis": "No specific threats were identified, since no data exposure was found for this email in the current investigation.",
                "business_impact": "There is no known business or personal impact at this time, as no breach was detected.",
                "attack_scenario": "No attack scenario applies, since no breach data is currently associated with this email.",
                "overall_assessment": "Continue practicing good password hygiene and re-check periodically.",
            },
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
            result = _call_ollama_once(prompt, data_types, has_password, has_financial, has_phone, risk_reduction)
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
    return _rule_based_fallback(breaches, risk_level, has_password, has_financial, has_phone, data_types, risk_reduction)


def format_mitigation_for_display(mitigation: Dict[str, Any]) -> Dict[str, Any]:
    """Format a generate_ai_mitigation() result for HTML template display."""
    risk_level = mitigation.get("risk_level", "MEDIUM")
    display = {
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
        "evidence_map": mitigation.get("evidence_map", []),
    }
    for key in REPORT_TEXT_DEFAULTS:
        display[key] = mitigation.get(key, REPORT_TEXT_DEFAULTS[key])
    if "risk_reduction" in mitigation:
        display["risk_reduction"] = mitigation["risk_reduction"]
    return display


def get_risk_emoji(risk_level: str) -> str:
    """Get emoji for risk level."""
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk_level, "⚪")


if __name__ == "__main__":
    test_breaches = [
        {"Name": "TestBreach", "BreachDate": "2024-01-01", "DataClasses": ["Email addresses", "Passwords"]},
    ]
    sample_risk_reduction = {
        "current_score": 55,
        "estimated_score": 30,
        "reduction_points": 25,
        "factors": [{"factor": "Password exposure", "points": 15, "neutralized_by": "Reset password + enable 2FA"}],
    }
    result = generate_ai_mitigation(
        "test@example.com", test_breaches, risk_score=55, risk_level="MEDIUM", risk_reduction=sample_risk_reduction
    )
    print(json.dumps(result, indent=2))
