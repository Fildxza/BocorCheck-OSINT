"""
AI Mitigation Module for BocorCheck
FILDZA_AI_ACTIVE - Provides dynamic AI-powered mitigation recommendations using Ollama (phi3)

This module handles:
- Connecting to local Ollama instance
- Generating risk assessments based on OSINT data
- Providing fallback static mitigations if AI unavailable
- Logging and debugging
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("bocorcheck.ai_mitigation")
logging.basicConfig(level=logging.INFO)

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"  # Lightweight model
OLLAMA_TIMEOUT = 40  # seconds

# Default static mitigations (fallback)
DEFAULT_MITIGATION = {
    "risk_level": "MEDIUM",
    "explanation": "Data breach detected. Immediate action recommended.",
    "mitigation": {
        "immediate": [
            "Change password for affected accounts",
            "Enable two-factor authentication (2FA)",
            "Monitor account for suspicious activity",
        ],
        "short_term": [
            "Review account access logs and active sessions",
            "Update security questions if available",
            "Set up breach monitoring alerts",
        ],
        "long_term": [
            "Use unique passwords for each account",
            "Implement password manager",
            "Regular security audits of online accounts",
        ],
    }
}


def generate_ai_mitigation(
    email: str,
    breaches: List[Dict[str, Any]],
    risk_score: Optional[int] = None
) -> Dict[str, Any]:
    """
    FILDZA_AI_ACTIVE - Generate AI-powered mitigation plan via Ollama phi3.
    
    Args:
        email: Email being analyzed
        breaches: List of breach dictionaries from HIBP
        risk_score: Optional risk score (0-100)
        
    Returns:
        Dictionary with risk_level, explanation, and mitigation plan
        Returns DEFAULT_MITIGATION if AI unavailable
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"FILDZA_AI_ACTIVE - AI Mitigation Generation Started")
    logger.info(f"{'='*60}")
    logger.info(f"Email: {email}")
    logger.info(f"Breaches: {len(breaches)}")
    
    if not breaches:
        logger.info("No breaches to analyze")
        return {
            "risk_level": "LOW",
            "explanation": "No known data breaches found for this email.",
            "mitigation": {
                "immediate": ["No immediate action required"],
                "short_term": ["Continue monitoring for new breaches"],
                "long_term": ["Maintain strong password practices"],
            }
        }
    
    # Extract data types
    data_types = sorted({d for b in breaches for d in b.get("DataClasses", [])})
    logger.info(f"Exposed data types: {', '.join(data_types) if data_types else 'Unknown'}")
    
    # Build breach summary
    breach_summary = ""
    for i, breach in enumerate(breaches, 1):
        breach_summary += f"\n{i}. {breach.get('Name', 'Unknown')}: {', '.join(breach.get('DataClasses', []))} (Date: {breach.get('BreachDate', 'Unknown')})"
    
    # Build optimized phi3 prompt
    prompt = f"""You are a cybersecurity expert. Analyze this breach data and respond ONLY with JSON.

BREACH DATA:
Email: {email}
Breaches: {len(breaches)}
Exposed: {', '.join(data_types) if data_types else 'Unknown'}{breach_summary}

For EACH mitigation action, make it SPECIFIC to the exposed data types:
- Password exposed? → Reset all passwords, enable 2FA
- Email exposed? → Check for unauthorized access, enable recovery options
- Financial data? → Monitor credit, place fraud alert, check credit reports
- Phone? → Check for SIM swap, monitor phone activity
- Address/Personal? → Monitor for identity theft, place fraud alert

PROVIDE ONLY THIS JSON (no other text):
{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "explanation": "Assessment based on specific breach data",
  "mitigation": {{
    "immediate": ["action 1 specific to breach", "action 2", "action 3"],
    "short_term": ["day 1-7 action specific to breach", "action 2", "action 3"],
    "long_term": ["ongoing monitoring", "security improvement", "verification"]
  }}
}}"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        logger.info(f"Connecting to Ollama at {OLLAMA_URL}")
        logger.info(f"Model: {OLLAMA_MODEL} | Timeout: {OLLAMA_TIMEOUT}s")
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        
        if response.status_code != 200:
            logger.error(f"❌ Ollama returned {response.status_code}: {response.text}")
            logger.warning("Using fallback mitigation")
            return DEFAULT_MITIGATION
        
        logger.info(f"✓ Ollama responded successfully")
        data = response.json()
        response_text = data.get("response", "")
        logger.info(f"Response length: {len(response_text)} characters")
        
        # Extract JSON
        start = response_text.find("{")
        end = response_text.rfind("}")
        
        if start == -1 or end == -1:
            logger.error(f"❌ No JSON in response")
            logger.warning("Using fallback mitigation")
            return DEFAULT_MITIGATION
        
        json_str = response_text[start:end+1]
        
        try:
            result = json.loads(json_str)
            
            # Validate structure
            if not all(k in result for k in ["risk_level", "explanation", "mitigation"]):
                logger.error(f"❌ Missing required keys")
                return DEFAULT_MITIGATION
            
            mitigation = result.get("mitigation", {})
            if not all(k in mitigation for k in ["immediate", "short_term", "long_term"]):
                logger.error(f"❌ Mitigation missing keys")
                return DEFAULT_MITIGATION
            
            logger.info(f"✓ FILDZA_AI_ACTIVE - Analysis successful")
            logger.info(f"  Risk Level: {result.get('risk_level')}")
            logger.info(f"  Actions: {len(mitigation.get('immediate', []))} immediate")
            logger.info(f"{'='*60}\n")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse failed: {e}")
            logger.warning("Using fallback mitigation")
            return DEFAULT_MITIGATION
            
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Cannot connect to Ollama")
        logger.error(f"Run: ollama run {OLLAMA_MODEL}")
        logger.warning("Using fallback mitigation")
        return DEFAULT_MITIGATION
    except requests.exceptions.Timeout:
        logger.error(f"❌ Ollama timeout ({OLLAMA_TIMEOUT}s)")
        logger.warning("Using fallback mitigation")
        return DEFAULT_MITIGATION
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.warning("Using fallback mitigation")
        return DEFAULT_MITIGATION


def format_mitigation_for_display(mitigation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format mitigation plan for HTML template display.
    
    Args:
        mitigation: Mitigation dictionary from generate_ai_mitigation()
        
    Returns:
        Formatted dictionary with HTML-safe strings
    """
    return {
        "risk_level": mitigation.get("risk_level", "MEDIUM"),
        "risk_color": {
            "HIGH": "danger",
            "MEDIUM": "warning",
            "LOW": "success"
        }.get(mitigation.get("risk_level", "MEDIUM"), "info"),
        "explanation": mitigation.get("explanation", ""),
        "immediate": mitigation.get("mitigation", {}).get("immediate", []),
        "short_term": mitigation.get("mitigation", {}).get("short_term", []),
        "long_term": mitigation.get("mitigation", {}).get("long_term", []),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ai_powered": True,
        "fildza_active": True
    }


def get_risk_emoji(risk_level: str) -> str:
    """Get emoji for risk level"""
    return {
        "HIGH": "🔴",
        "MEDIUM": "🟡",
        "LOW": "🟢"
    }.get(risk_level, "⚪")


if __name__ == "__main__":
    # Test the module
    test_breaches = [
        {
            "Name": "TestBreach",
            "BreachDate": "2024-01-01",
            "DataClasses": ["Email", "Password"]
        }
    ]
    result = generate_ai_mitigation("test@example.com", test_breaches)
    print(json.dumps(result, indent=2))
