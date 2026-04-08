import os
import csv
from io import StringIO
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import phonenumbers
import requests
from flask import Flask, render_template, request, redirect, url_for, session, Response, g
from mysql.connector import Error as MySQLError
from mysql.connector import connect

from auth import (
    create_user,
    login_user,
    get_user_by_id,
    check_user_exists,
)

from mitigation import (
    get_smart_recommendations,
    get_malaysian_resources,
    format_mitigation_for_display,
    calculate_total_time,
)

from monitoring import (
    create_monitoring_subscription,
    get_user_monitoring,
    get_breach_timeline,
    get_timeline_statistics,
    update_monitoring_check,
)

from darkweb_checker import (
    check_darkweb_mock,
    record_darkweb_finding,
    get_darkweb_findings,
    get_investigation_darkweb_findings,
    calculate_darkweb_risk_score,
)

from data_analyzer import (
    analyze_breach_datatypes,
    detect_hash_algorithm,
    calculate_crack_risk,
    generate_forensic_report,
    store_enhanced_breach_details,
    get_data_type_risk_reference,
    get_hash_algorithm_reference,
)


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-for-production")

# Session security configuration
app.config['SESSION_COOKIE_SECURE'] = os.getenv("FLASK_ENV") == "production"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2 hours

# Login required decorator for protected routes
def login_required(f):
    """
    Decorator to require login for protected routes.
    Redirects to login page if user not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Replace this with your real HIBP API key for local testing.
# Recommended: keep it in an environment variable instead of hardcoding.
API_KEY = os.getenv("HIBP_API_KEY", "YOUR_HIBP_API_KEY_HERE")
HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount"
REQUEST_TIMEOUT_SECONDS = 15
PHONE_DEFAULT_REGION = os.getenv("PHONE_DEFAULT_REGION", "MY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

SUPPORTED_LANGUAGES = ("en", "ms")
DEFAULT_LANGUAGE = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "dashboard_title": "BocorCheck Dashboard",
        "dashboard_subtitle": "Personal Data Breach Discovery using HIBP API v3",
        "view_history": "View History",
        "admin_logout": "Admin Logout",
        "admin_login": "Admin Login",
        "mock_mode_active": "Mock Data Mode Active.",
        "mock_mode_notice": "This is only an FYP demo attempt without API.",
        "language": "Language",
        "english": "English",
        "malay": "Malay",
        "email_address": "Email Address",
        "phone_number": "Phone Number",
        "bank_account_demo": "Bank Account (Demo)",
        "analyze": "Analyze",
        "send_telegram_test": "Send Telegram Test",
        "data_source_mode": "Data Source Mode",
        "auto": "Auto",
        "mock": "Mock",
        "live_hibp": "Live (HIBP API)",
        "effective_mode": "Current effective mode:",
        "telegram_not_configured": "Telegram test not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment variables.",
        "investigation_summary": "Investigation Summary",
        "email_checked": "Email Checked",
        "phone_checked": "Phone Number Checked",
        "bank_checked": "Bank Account Checked (Demo)",
        "total_breaches": "Total Breaches Found",
        "risk_level": "Risk Level",
        "risk_score": "Risk Score",
        "score_of": "Score: {score} / 100",
        "phone_osint_check": "Phone Number OSINT Check",
        "valid_format": "Valid Format",
        "country_code": "Country Code",
        "region": "Region",
        "phone_exposed": "Phone Exposed",
        "yes": "Yes",
        "no": "No",
        "bank_exposure_demo": "Bank Exposure Demo (Malaysia Context)",
        "format_valid": "Format Valid",
        "masked_account": "Masked Account",
        "exposure_status": "Exposure Status",
        "exposed_mock": "Exposed (Mock)",
        "no_exposure_mock": "No Exposure (Mock)",
        "data_source": "Data Source",
        "mock_dataset": "Mock Dataset",
        "bank_invalid": "Bank account format invalid. Please enter 10 to 16 digits.",
        "breach_incidents": "Breach Incidents Found",
        "overall_risk": "Overall Risk: {level}",
        "company_breach": "Company / Breach",
        "date": "Date",
        "data_classes": "Data Classes Leaked",
        "risk": "Risk",
        "recommended_mitigation": "Recommended Mitigation Plan",
        "login_title": "Admin Login",
        "login_subtitle": "Sign in to access investigation history.",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "back_dashboard": "Back to Dashboard",
        "history_title": "Investigation History",
        "history_subtitle": "Filter by date and risk level, then export as CSV.",
        "dashboard": "Dashboard",
        "logout": "Logout",
        "start_date": "Start Date",
        "end_date": "End Date",
        "all": "All",
        "apply_filter": "Apply Filter",
        "export_csv": "Export CSV",
        "id": "ID",
        "email": "Email",
        "breaches": "Breaches",
        "checked_at": "Checked At",
        "no_logs_found": "No investigation logs found.",
    },
    "ms": {
        "dashboard_title": "BocorCheck Dashboard",
        "dashboard_subtitle": "Penemuan Kebocoran Data Peribadi menggunakan API HIBP v3",
        "view_history": "Lihat Sejarah",
        "admin_logout": "Log Keluar Admin",
        "admin_login": "Log Masuk Admin",
        "mock_mode_active": "Mod Data Mock Aktif.",
        "mock_mode_notice": "Ini hanya cubaan demo FYP tanpa API.",
        "language": "Bahasa",
        "english": "Inggeris",
        "malay": "Melayu",
        "email_address": "Alamat Emel",
        "phone_number": "Nombor Telefon",
        "bank_account_demo": "Akaun Bank (Demo)",
        "analyze": "Analisis",
        "send_telegram_test": "Hantar Ujian Telegram",
        "data_source_mode": "Mod Sumber Data",
        "auto": "Auto",
        "mock": "Mock",
        "live_hibp": "Live (API HIBP)",
        "effective_mode": "Mod semasa digunakan:",
        "telegram_not_configured": "Ujian Telegram belum dikonfigurasikan. Tetapkan TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID dalam pembolehubah persekitaran.",
        "investigation_summary": "Ringkasan Siasatan",
        "email_checked": "Emel Disemak",
        "phone_checked": "Nombor Telefon Disemak",
        "bank_checked": "Akaun Bank Disemak (Demo)",
        "total_breaches": "Jumlah Kebocoran Ditemui",
        "risk_level": "Tahap Risiko",
        "risk_score": "Skor Risiko",
        "score_of": "Skor: {score} / 100",
        "phone_osint_check": "Semakan OSINT Nombor Telefon",
        "valid_format": "Format Sah",
        "country_code": "Kod Negara",
        "region": "Wilayah",
        "phone_exposed": "Telefon Terdedah",
        "yes": "Ya",
        "no": "Tidak",
        "bank_exposure_demo": "Demo Pendedahan Akaun Bank (Konteks Malaysia)",
        "format_valid": "Format Sah",
        "masked_account": "Akaun Bertopeng",
        "exposure_status": "Status Pendedahan",
        "exposed_mock": "Terdedah (Mock)",
        "no_exposure_mock": "Tiada Pendedahan (Mock)",
        "data_source": "Sumber Data",
        "mock_dataset": "Dataset Mock",
        "bank_invalid": "Format akaun bank tidak sah. Sila masukkan 10 hingga 16 digit.",
        "breach_incidents": "Insiden Kebocoran Ditemui",
        "overall_risk": "Risiko Keseluruhan: {level}",
        "company_breach": "Syarikat / Kebocoran",
        "date": "Tarikh",
        "data_classes": "Kelas Data Bocor",
        "risk": "Risiko",
        "recommended_mitigation": "Pelan Mitigasi Disyorkan",
        "login_title": "Log Masuk Admin",
        "login_subtitle": "Log masuk untuk akses sejarah siasatan.",
        "username": "Nama Pengguna",
        "password": "Kata Laluan",
        "login": "Log Masuk",
        "back_dashboard": "Kembali ke Dashboard",
        "history_title": "Sejarah Siasatan",
        "history_subtitle": "Tapis mengikut tarikh dan tahap risiko, kemudian eksport sebagai CSV.",
        "dashboard": "Dashboard",
        "logout": "Log Keluar",
        "start_date": "Tarikh Mula",
        "end_date": "Tarikh Akhir",
        "all": "Semua",
        "apply_filter": "Guna Penapis",
        "export_csv": "Eksport CSV",
        "id": "ID",
        "email": "Emel",
        "breaches": "Kebocoran",
        "checked_at": "Masa Semakan",
        "no_logs_found": "Tiada rekod siasatan ditemui.",
    },
}


def _resolve_language() -> str:
    preferred = (
        request.args.get("lang")
        or request.form.get("lang")
        or session.get("lang")
        or DEFAULT_LANGUAGE
    )
    preferred = preferred.lower().strip()
    if preferred not in SUPPORTED_LANGUAGES:
        preferred = DEFAULT_LANGUAGE
    session["lang"] = preferred
    return preferred


def tr(key: str, **kwargs: Any) -> str:
    lang = getattr(g, "lang", DEFAULT_LANGUAGE)
    bundle = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    fallback = TRANSLATIONS[DEFAULT_LANGUAGE]
    text = bundle.get(key) or fallback.get(key) or key
    if kwargs:
        return text.format(**kwargs)
    return text


@app.before_request
def set_language_context() -> None:
    g.lang = _resolve_language()
    
    # Load user data if logged in
    if 'user_id' in session:
        g.user = get_user_by_id(session['user_id'])
    else:
        g.user = None


@app.context_processor
def inject_i18n_context() -> Dict[str, Any]:
    return {
        "t": tr,
        "current_lang": getattr(g, "lang", DEFAULT_LANGUAGE),
        "supported_languages": SUPPORTED_LANGUAGES,
        "current_user": getattr(g, "user", None),
    }

# Temporary demo fallback for Telegram integration.
# Revoke and replace after presentation.
DEMO_TELEGRAM_TOKEN = "8784573630:AAGHKXGUIdZLzVgE0L1aZkM1uzz0_r5o9Bk"
DEMO_TELEGRAM_CHAT_ID = "5917103363"

MYSQL_DEFAULTS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "fyp_user",
    "password": "Admin123!",
    "database": "fyp_osint",
}

# DB logging is enabled by default so investigation, risk_scores, and alerts
# are persisted even when app.py is started directly without env bootstrapping.
# Set ENABLE_DB_LOGGING=false only when intentionally running in DB-offline mode.
ENABLE_DB_LOGGING = os.getenv("ENABLE_DB_LOGGING", "true").lower() == "true"

# Mock mode helps local demo when API key is not available yet.
# It can be forced via USE_MOCK_DATA=true in environment variables.
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Hardcoded prototype dataset for thesis demo with realistic Malaysian-context labels.
MOCK_BREACHES: Dict[str, Dict[str, Any]] = {
    "fildza@ur.unirazak.edu.my": {
        "status": "Breached",
        "risk_score": 45,
        "risk_level": "MEDIUM",
        "sources": [
            {
                "Name": "EduForumDemo",
                "BreachDate": "2024-02-11",
                "DataClasses": ["Email addresses", "Passwords"],
            }
        ],
    },
    "amin.demo@gmail.com": {
        "status": "Breached",
        "risk_score": 95,
        "risk_level": "HIGH",
        "sources": [
            {
                "Name": "ShopLink",
                "BreachDate": "2023-08-03",
                "DataClasses": ["Email addresses", "Passwords", "Full names"],
            },
            {
                "Name": "PayTrack",
                "BreachDate": "2022-11-19",
                "DataClasses": ["Financial Information", "Phone numbers"],
            },
            {
                "Name": "RewardsPortal",
                "BreachDate": "2021-01-14",
                "DataClasses": ["Passwords", "Date of birth"],
            },
        ],
    },
    "nur.safe@example.com": {
        "status": "Safe",
        "risk_score": 10,
        "risk_level": "LOW",
        "sources": [],
    },
    "amir.jobseek@gmail.com": {
        "status": "Breached",
        "risk_score": 55,
        "risk_level": "MEDIUM",
        "sources": [
            {
                "Name": "MyJobPortal-MY",
                "BreachDate": "2024-05-28",
                "DataClasses": ["Email addresses", "Phone numbers", "Address"],
            }
        ],
    },
    "siti.telco@outlook.com": {
        "status": "Breached",
        "risk_score": 70,
        "risk_level": "MEDIUM",
        "sources": [
            {
                "Name": "LocalTelco-Leaked",
                "BreachDate": "2023-04-02",
                "DataClasses": ["Phone numbers", "Address", "Date of birth"],
            }
        ],
    },
    "farid.wallet@yahoo.com": {
        "status": "Breached",
        "risk_score": 90,
        "risk_level": "HIGH",
        "sources": [
            {
                "Name": "E-Wallet-Mega-Breach",
                "BreachDate": "2025-01-07",
                "DataClasses": [
                    "Financial Information",
                    "Passwords",
                    "Full names",
                    "Phone numbers",
                ],
            }
        ],
    },
    "intan.professional@proton.me": {
        "status": "Breached",
        "risk_score": 83,
        "risk_level": "HIGH",
        "sources": [
            {
                "Name": "LinkedIn-RegionalDump",
                "BreachDate": "2021-06-24",
                "DataClasses": ["Email addresses", "Full names", "Usernames"],
            }
        ],
    },
    "hafiz.lowrisk@example.com": {
        "status": "Breached",
        "risk_score": 20,
        "risk_level": "LOW",
        "sources": [
            {
                "Name": "NewsletterHub",
                "BreachDate": "2021-11-07",
                "DataClasses": ["Email addresses", "Usernames"],
            }
        ],
    },
    "mfildxza@gmail.com": {
        "status": "Breached",
        "risk_score": 68,
        "risk_level": "MEDIUM",
        "sources": [
            {
                "Name": "Shoppe-Marketplace",
                "BreachDate": "2024-09-16",
                "DataClasses": ["Email addresses", "Phone numbers"],
            },
            {
                "Name": "MyJobPortal-MY",
                "BreachDate": "2023-12-01",
                "DataClasses": ["Phone numbers", "Address", "Date of birth"],
            },
        ],
    },
}

# Backward-compatible alias used by existing templates and routes.
MOCK_BREACH_DATA: Dict[str, List[Dict[str, Any]]] = {
    email: profile.get("sources", []) for email, profile in MOCK_BREACHES.items()
}

MOCK_PHONE_BREACH_DATA: Dict[str, List[Dict[str, Any]]] = {
    "+60123456789": [
        {
            "Name": "MyShopDelivery",
            "BreachDate": "2024-07-20",
            "DataClasses": ["Phone numbers", "Email addresses"],
        }
    ],
    "+60135550011": [
        {
            "Name": "LocalTelco-Leaked",
            "BreachDate": "2023-10-09",
            "DataClasses": ["Phone numbers", "Address"],
        },
        {
            "Name": "E-Wallet-Mega-Breach",
            "BreachDate": "2025-01-07",
            "DataClasses": ["Phone numbers", "Financial Information"],
        }
    ],
    "+601136005936": [
        {
            "Name": "Shoppe-Marketplace",
            "BreachDate": "2024-09-16",
            "DataClasses": ["Phone numbers", "Email addresses"],
        },
        {
            "Name": "LocalTelco-Leaked",
            "BreachDate": "2023-06-21",
            "DataClasses": ["Phone numbers", "Address"],
        },
    ],
}

# Demo-only mock exposure dataset for banking account checks.
# This is intentionally synthetic and should not be treated as real intelligence.
MOCK_BANK_EXPOSURE_DATA: Dict[str, Dict[str, str]] = {
    "123456789012": {
        "source": "DemoLeakArchive2024",
        "note": "Simulated exposure in a leaked account registry sample.",
    },
    "987654321098": {
        "source": "DemoFinanceDump2023",
        "note": "Simulated exposure for thesis demonstration only.",
    },
}
MOCK_BANK_ACCOUNT_SAMPLES = ["1234-5678-9012", "987654321098"]


def is_mock_mode_enabled() -> bool:
    """
    Enable mock mode when explicitly requested or when API key is still placeholder.
    """
    return USE_MOCK_DATA or API_KEY == "YOUR_HIBP_API_KEY_HERE"


def resolve_api_mode(selected_mode: str) -> str:
    """
    Resolve API mode from form input.
    Allowed: auto, mock, live.
    """
    mode = (selected_mode or "auto").strip().lower()
    if mode in {"auto", "mock", "live"}:
        return mode
    return "auto"


def should_use_mock_data(mode: str) -> bool:
    if mode == "mock":
        return True
    if mode == "live":
        return False
    return is_mock_mode_enabled()


def is_admin_logged_in() -> bool:
    return bool(session.get("is_admin"))


def get_telegram_config() -> Dict[str, str]:
    """
    Read Telegram settings at runtime so updated env vars are picked up immediately.
    """
    return {
        "token": os.getenv("TELEGRAM_BOT_TOKEN", DEMO_TELEGRAM_TOKEN).strip(),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", DEMO_TELEGRAM_CHAT_ID).strip(),
    }


def is_telegram_configured() -> bool:
    cfg = get_telegram_config()
    return bool(cfg["token"] and cfg["chat_id"])


def _normalize_bank_account(account_input: str) -> str:
    return "".join(ch for ch in account_input if ch.isdigit())


def analyze_bank_account(account_input: str) -> Dict[str, Any]:
    """
    Demo-only bank account exposure module.
    - Checks basic numeric format (10-16 digits).
    - Matches against mock exposure dataset.
    - Returns disclaimer suitable for academic presentation.
    """
    normalized = _normalize_bank_account(account_input)
    is_valid = 10 <= len(normalized) <= 16
    exposure = MOCK_BANK_EXPOSURE_DATA.get(normalized)

    return {
        "input": account_input,
        "normalized": normalized if is_valid else None,
        "is_valid": is_valid,
        "last4": normalized[-4:] if normalized else None,
        "is_exposed": bool(exposure),
        "source": exposure.get("source") if exposure else None,
        "note": exposure.get("note") if exposure else None,
        "disclaimer": (
            "Bank account exposure check uses synthetic mock data for FYP demo only. "
            "No real banking system lookup is performed."
        ),
    }


def send_telegram_test_alert(
    email: str,
    phone_number: str,
    data_mode: str,
    bank_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Send a simple Telegram test alert from dashboard for presentation demo.
    """
    cfg = get_telegram_config()
    token = cfg["token"]
    chat_id = cfg["chat_id"]

    if not token or not chat_id:
        return {
            "ok": False,
            "message": "Telegram token/chat ID not configured in environment variables.",
        }

    lines = [
        "OSINT Dashboard Test Alert",
        f"Mode: {data_mode}",
        f"Email: {email or '-'}",
        f"Phone: {phone_number or '-'}",
    ]

    if bank_result and bank_result.get("input"):
        lines.append(f"Bank Account (demo): {bank_result.get('input')}")
        lines.append(
            "Bank Exposure (demo): "
            + ("Exposed" if bank_result.get("is_exposed") else "Not exposed")
        )

    payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines),
    }

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            return {"ok": False, "message": "Telegram API rejected the message."}
        return {"ok": True, "message": "Telegram test alert sent successfully."}
    except requests.RequestException:
        return {"ok": False, "message": "Failed to send Telegram alert. Check network/token."}


def send_telegram_alert(
    email: str,
    risk_score: int,
    risk_level: str,
    breach_count: int,
) -> Dict[str, Any]:
    """
    Send automatic Telegram alert when risk_score >= 70.
    Required message fields: email, risk score, risk level, breach count.
    """
    cfg = get_telegram_config()
    token = cfg["token"]
    chat_id = cfg["chat_id"]

    if not token or not chat_id:
        return {
            "ok": False,
            "message": "Telegram token/chat ID not configured in environment variables.",
        }

    level_upper = (risk_level or "LOW").strip().upper()
    if level_upper == "HIGH":
        risk_level_label = "High"
    elif level_upper == "MEDIUM":
        risk_level_label = "Medium"
    else:
        risk_level_label = "Low"

    message_lines = [
        "OSINT Auto Alert",
        f"Email: {email or '-'}",
        f"Risk Score: {risk_score}",
        f"Risk Level: {risk_level_label}",
        f"Breaches: {breach_count}",
    ]

    payload = {
        "chat_id": chat_id,
        "text": "\n".join(message_lines),
    }

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            return {"ok": False, "message": "Telegram API rejected the auto-alert."}
        return {"ok": True, "message": "Auto Telegram alert sent successfully."}
    except requests.RequestException:
        return {"ok": False, "message": "Failed to send auto Telegram alert."}


def query_mock_breaches(email: str) -> List[Dict[str, Any]]:
    """
    Return hardcoded breach records for demo emails.
    Unknown emails default to no breach for safe-message demonstration.
    """
    profile = MOCK_BREACHES.get(email.lower(), {})
    return profile.get("sources", [])


def query_mock_phone_breaches(phone_number: str) -> List[Dict[str, Any]]:
    """
    Return hardcoded breach records for demo phone numbers.
    """
    return MOCK_PHONE_BREACH_DATA.get(phone_number, [])


def check_email_logic(
    email: str,
    phone_number: str = "",
    use_mock: bool = True,
) -> Dict[str, Any]:
    """
    Consolidated lookup logic for email and optional phone checks.
    In mock mode, prefer explicit risk scores from MOCK_BREACHES and return
    phone exposure source details for realistic demo behavior.
    """
    normalized_email = (email or "").strip().lower()
    normalized_phone = (phone_number or "").strip()

    breaches: List[Dict[str, Any]] = []
    phone_breaches: List[Dict[str, Any]] = []
    message = None
    risk_score = 10
    risk_level = "LOW"

    if use_mock:
        profile = MOCK_BREACHES.get(normalized_email, None)
        if profile:
            breaches.extend(profile.get("sources", []))
            risk_score = int(profile.get("risk_score", 10))
            risk_level = str(profile.get("risk_level", "LOW")).upper()

        if normalized_phone:
            phone_breaches = query_mock_phone_breaches(normalized_phone)
            breaches.extend(phone_breaches)

        if phone_breaches and risk_score < 40:
            risk_score = 40
            risk_level = "MEDIUM"
    else:
        if normalized_email:
            breaches = query_hibp_breaches(email=normalized_email, api_key=API_KEY)
        if normalized_phone and not normalized_email:
            message = (
                "Phone OSINT completed. Live breach lookup requires email input "
                "on HIBP v3 account endpoint."
            )

        dynamic_risk = calculate_risk_score(
            {
                "breaches": breaches,
                "phone_exposed": _contains_phone_exposure(breaches),
            }
        )
        risk_score = dynamic_risk["risk_score"]
        risk_level = dynamic_risk["risk_level"]

    unique: Dict[str, Dict[str, Any]] = {}
    for breach in breaches:
        unique[breach.get("Name", "Unknown")] = breach
    deduped_breaches = list(unique.values())

    phone_exposed_sources = [
        {
            "source": breach.get("Name", "Unknown"),
            "breach_date": breach.get("BreachDate", "Unknown"),
            "data_classes": breach.get("DataClasses", []),
        }
        for breach in phone_breaches
    ]

    return {
        "email": normalized_email,
        "phone_number": normalized_phone,
        "breaches": deduped_breaches,
        "has_breach": bool(deduped_breaches),
        "phone_exposed": bool(phone_breaches),
        "phone_exposed_sources": phone_exposed_sources,
        "risk_score": max(1, min(100, int(risk_score))),
        "risk_level": str(risk_level).upper(),
        "message": message,
    }


def query_hibp_breaches(email: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Query the HIBP v3 breached account endpoint for a specific email.

    Returns:
        - List of breaches when found.
        - Empty list when no breaches are found (404 from HIBP).
    Raises:
        requests.HTTPError for unexpected non-404 API errors.
    """
    headers = {
        "hibp-api-key": api_key,
        "user-agent": "fyp-osint-dashboard-prototype",
    }

    # truncateResponse=false returns richer breach details for dashboard display.
    params = {"truncateResponse": "false"}

    response = requests.get(
        f"{HIBP_URL}/{email}",
        headers=headers,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code == 404:
        return []

    response.raise_for_status()
    return response.json()


def calculate_risk(data_classes: List[str]) -> str:
    """
    Data-class risk logic for thesis prototype:
    - High: any of Passwords, Full Names, Financial Information.
    - Medium: any of Phone Numbers, Address, Date of Birth.
    - Low: only Email Addresses/Usernames.
    """
    normalized = {item.strip().lower() for item in data_classes}

    has_high = (
        "passwords" in normalized
        or "full names" in normalized
        or any("financial" in item for item in normalized)
    )

    if has_high:
        return "High"

    has_medium = (
        "phone numbers" in normalized
        or "phone number" in normalized
        or "address" in normalized
        or "date of birth" in normalized
    )

    if has_medium:
        return "Medium"

    if normalized.issubset({"email addresses", "usernames"}):
        return "Low"

    return "Medium"


def analyze_phone_number(phone_input: str) -> Dict[str, Optional[str]]:
    """
    Basic phone OSINT helper:
    - Validates format.
    - Extracts country code and region.
    - Returns normalized E.164 form when valid.
    """
    result: Dict[str, Optional[str]] = {
        "input": phone_input,
        "normalized": None,
        "is_valid": False,
        "country_code": None,
        "region": None,
    }

    if not phone_input:
        return result

    try:
        parsed = phonenumbers.parse(phone_input, PHONE_DEFAULT_REGION)
        is_valid = phonenumbers.is_valid_number(parsed)
        result["is_valid"] = is_valid
        result["country_code"] = f"+{parsed.country_code}"
        result["region"] = phonenumbers.region_code_for_number(parsed)

        if is_valid:
            result["normalized"] = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
    except phonenumbers.NumberParseException:
        result["is_valid"] = False

    return result


def _contains_password_exposure(breaches: List[Dict[str, Any]]) -> bool:
    for breach in breaches:
        data_classes = [item.lower() for item in breach.get("DataClasses", [])]
        if "passwords" in data_classes:
            return True
    return False


def _contains_phone_exposure(breaches: List[Dict[str, Any]]) -> bool:
    for breach in breaches:
        data_classes = [item.lower() for item in breach.get("DataClasses", [])]
        if "phone numbers" in data_classes or "phone number" in data_classes:
            return True
    return False


def _has_recent_breach(breaches: List[Dict[str, Any]]) -> bool:
    cutoff_year = date.today().year - 3
    for breach in breaches:
        breach_date = breach.get("BreachDate")
        if not breach_date:
            continue
        try:
            parsed = datetime.strptime(breach_date, "%Y-%m-%d").date()
            if parsed.year >= cutoff_year:
                return True
        except ValueError:
            continue
    return False


def calculate_risk_score(breach_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute risk score (0-100) and level:
    +20 per breach
    +15 if password exposure exists
    +10 if phone number exposure exists
    +10 if any breach occurred within last 3 years
    """
    breaches = breach_data.get("breaches", [])
    phone_exposed = breach_data.get("phone_exposed", False)

    score = 0
    score += len(breaches) * 20

    if _contains_password_exposure(breaches):
        score += 15

    if phone_exposed or _contains_phone_exposure(breaches):
        score += 10

    if _has_recent_breach(breaches):
        score += 10

    score = min(score, 100)

    if score <= 30:
        level = "LOW"
    elif score <= 60:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {"risk_score": score, "risk_level": level}


def generate_risk_explanation(
    risk_score: int,
    risk_level: str,
    breach_count: int,
    sensitive_data: bool,
) -> str:
    """
    Generate a concise risk explanation for DB logging and reporting.
    """
    level = (risk_level or "LOW").strip().upper()
    level_label = "High" if level == "HIGH" else ("Medium" if level == "MEDIUM" else "Low")
    sensitive_text = "sensitive data exposure detected" if sensitive_data else "no sensitive data exposure detected"
    return (
        f"{level_label} risk due to {breach_count} breach(es); "
        f"risk score {risk_score}; {sensitive_text}."
    )


def has_sensitive_data_exposure(breaches: List[Dict[str, Any]]) -> bool:
    """
    Determine if breach data contains sensitive classes.
    """
    sensitive_markers = {
        "passwords",
        "financial information",
        "credit cards",
        "payment history",
        "phone numbers",
        "date of birth",
        "full names",
    }
    for breach in breaches:
        for data_class in breach.get("DataClasses", []):
            if data_class.strip().lower() in sensitive_markers:
                return True
    return False


def get_db_connection():
    """
    Create MySQL connection from environment configuration.
    """
    if not ENABLE_DB_LOGGING:
        raise MySQLError(msg="DB logging disabled (ENABLE_DB_LOGGING=false).")

    config = {
        "host": os.getenv("MYSQL_HOST", MYSQL_DEFAULTS["host"]),
        "port": int(os.getenv("MYSQL_PORT", str(MYSQL_DEFAULTS["port"]))),
        "user": os.getenv("MYSQL_USER", MYSQL_DEFAULTS["user"]),
        "password": os.getenv("MYSQL_PASSWORD", MYSQL_DEFAULTS["password"]),
        "database": os.getenv("MYSQL_DATABASE", MYSQL_DEFAULTS["database"]),
        # Avoid mysql-connector C-extension instability on some Windows setups.
        "use_pure": True,
    }

    try:
        return connect(**config)
    except MySQLError:
        # Local dev fallback: if env is missing/wrong, retry using known FYP defaults.
        fallback = {
            "host": MYSQL_DEFAULTS["host"],
            "port": MYSQL_DEFAULTS["port"],
            "user": MYSQL_DEFAULTS["user"],
            "password": MYSQL_DEFAULTS["password"],
            "database": MYSQL_DEFAULTS["database"],
            "use_pure": True,
        }
        return connect(**fallback)


def init_db() -> None:
    """
    Initialize required tables including users table for authentication.
    """
    create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        INDEX idx_users_email (email),
        INDEX idx_users_username (username),
        INDEX idx_users_created_at (created_at)
    ) ENGINE=InnoDB
    """

    create_investigation_logs = """
    CREATE TABLE IF NOT EXISTS investigation_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        email VARCHAR(255) NULL,
        phone_number VARCHAR(32) NULL,
        breach_count INT NOT NULL,
        risk_score INT NOT NULL,
        risk_level VARCHAR(10) NOT NULL,
        checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_investigation_user
            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE SET NULL,
        INDEX idx_investigation_user_id (user_id),
        INDEX idx_investigation_checked_at (checked_at),
        INDEX idx_investigation_risk_level (risk_level),
        INDEX idx_investigation_email (email)
    ) ENGINE=InnoDB
    """

    create_breach_results = """
    CREATE TABLE IF NOT EXISTS breach_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        investigation_id INT NOT NULL,
        breach_name VARCHAR(255) NOT NULL,
        breach_date DATE NULL,
        data_exposed TEXT,
        FOREIGN KEY (investigation_id) REFERENCES investigation_logs(id) ON DELETE CASCADE,
        INDEX idx_breach_investigation_id (investigation_id),
        INDEX idx_breach_date (breach_date)
    ) ENGINE=InnoDB
    """

    create_login_logs = """
    CREATE TABLE IF NOT EXISTS login_logs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        ip_address VARCHAR(64) NOT NULL,
        user_agent VARCHAR(512) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_login_logs_username (username),
        INDEX idx_login_logs_action (action),
        INDEX idx_login_logs_created_at (created_at)
    ) ENGINE=InnoDB
    """

    create_risk_scores = """
    CREATE TABLE IF NOT EXISTS risk_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        investigation_id INT NOT NULL,
        breach_count INT,
        sensitive_data BOOLEAN,
        risk_score INT,
        risk_level VARCHAR(10),
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
        INDEX idx_risk_scores_investigation_id (investigation_id),
        INDEX idx_risk_scores_level (risk_level),
        INDEX idx_risk_scores_created_at (created_at)
    ) ENGINE=InnoDB
    """

    create_alerts = """
    CREATE TABLE IF NOT EXISTS alerts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        investigation_id INT NOT NULL,
        alert_type VARCHAR(50),
        message TEXT,
        status VARCHAR(20),
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (investigation_id)
        REFERENCES investigation_logs(id)
        ON DELETE CASCADE,
        INDEX idx_alerts_investigation_id (investigation_id),
        INDEX idx_alerts_status (status),
        INDEX idx_alerts_sent_at (sent_at),
        UNIQUE KEY uq_alert_per_investigation_type (investigation_id, alert_type)
    ) ENGINE=InnoDB
    """

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_users)
            cursor.execute(create_investigation_logs)
            cursor.execute(create_breach_results)
            cursor.execute(create_login_logs)
            cursor.execute(create_risk_scores)
            cursor.execute(create_alerts)
        conn.commit()


def log_user_activity(username: str, role: str, action: str) -> None:
    """
    Persist login activity events to MySQL.
    Uses Flask request context to capture client IP and User-Agent.
    """
    insert_log = """
    INSERT INTO login_logs (username, role, action, ip_address, user_agent)
    VALUES (%s, %s, %s, %s, %s)
    """

    safe_username = (username or "unknown").strip()[:255]
    safe_role = (role or "unknown").strip()[:50]
    safe_action = (action or "unknown").strip()[:50]
    ip_address = (request.remote_addr or "unknown")[:64]
    user_agent = (request.headers.get("User-Agent") or "unknown")[:512]

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_log,
                (safe_username, safe_role, safe_action, ip_address, user_agent),
            )
        conn.commit()


def save_investigation(
    email: str,
    phone_number: str,
    breaches: List[Dict[str, Any]],
    risk_score: int,
    risk_level: str,
    user_id: Optional[int] = None,
) -> int:
    """
    Persist one investigation summary and its breach details in MySQL.
    Links investigation to user if user_id provided.
    """
    insert_log = """
    INSERT INTO investigation_logs (user_id, email, phone_number, breach_count, risk_score, risk_level)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    insert_breach = """
    INSERT INTO breach_results (investigation_id, breach_name, breach_date, data_exposed)
    VALUES (%s, %s, %s, %s)
    """

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_log,
                (
                    user_id,
                    email or None,
                    phone_number or None,
                    len(breaches),
                    risk_score,
                    risk_level,
                ),
            )
            investigation_id = cursor.lastrowid

            for breach in breaches:
                cursor.execute(
                    insert_breach,
                    (
                        investigation_id,
                        breach.get("Name", "Unknown"),
                        breach.get("BreachDate") or None,
                        ", ".join(breach.get("DataClasses", [])),
                    ),
                )

        conn.commit()
    return investigation_id


def save_risk_score(
    investigation_id: int,
    breach_count: int,
    sensitive_data: bool,
    risk_score: int,
    risk_level: str,
    explanation: str,
) -> None:
    """
    Persist computed risk scoring details.
    """
    insert_risk = """
    INSERT INTO risk_scores (
        investigation_id, breach_count, sensitive_data, risk_score, risk_level, explanation
    ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_risk,
                (
                    investigation_id,
                    breach_count,
                    1 if sensitive_data else 0,
                    risk_score,
                    risk_level,
                    explanation,
                ),
            )
        conn.commit()


def has_alert_for_investigation(investigation_id: int, alert_type: str) -> bool:
    """
    Prevent duplicate alerts for the same investigation and alert type.
    """
    query = """
    SELECT 1 FROM alerts
    WHERE investigation_id = %s AND alert_type = %s
    LIMIT 1
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (investigation_id, alert_type))
            return cursor.fetchone() is not None


def log_alert(
    investigation_id: int,
    alert_type: str,
    message: str,
    status: str,
) -> None:
    """
    Persist alert delivery log.
    """
    insert_alert = """
    INSERT INTO alerts (investigation_id, alert_type, message, status)
    VALUES (%s, %s, %s, %s)
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_alert, (investigation_id, alert_type, message, status))
        conn.commit()


def fetch_investigation_history(
    start_date: str = "",
    end_date: str = "",
    risk_level: str = "",
    user_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Get investigation logs with optional date and risk filters.
    If user_id is provided, only fetches that user's investigations.
    """
    query = """
    SELECT id, email, phone_number, breach_count, risk_score, risk_level, checked_at
    FROM investigation_logs
    WHERE 1=1
    """
    params: List[Any] = []

    # User isolation: only show user's own investigations
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)

    if start_date:
        query += " AND DATE(checked_at) >= %s"
        params.append(start_date)

    if end_date:
        query += " AND DATE(checked_at) <= %s"
        params.append(end_date)

    if risk_level:
        query += " AND risk_level = %s"
        params.append(risk_level.upper())

    query += " ORDER BY checked_at DESC LIMIT 500"

    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


def _risk_level_from_score(score: int) -> str:
    if score >= 75:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _normalize_timeline_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize timeline records so template/chart can rely on consistent keys.
    Works for both DB records and fallback records.
    """
    raw_score = event.get("current_risk_score")
    if raw_score is None:
        raw_score = event.get("initial_risk_score")
    if raw_score is None:
        raw_score = event.get("risk_score", 50)

    try:
        risk_score = int(raw_score)
    except (TypeError, ValueError):
        risk_score = 50

    breach_date = event.get("breach_date")
    discovery_date = event.get("discovery_date")

    time_to_discovery = event.get("time_to_discovery")
    if time_to_discovery is None and breach_date and discovery_date:
        try:
            time_to_discovery = (discovery_date - breach_date).days
        except TypeError:
            time_to_discovery = None

    normalized = {
        "breach_name": event.get("breach_name", "Unknown Breach"),
        "breach_date": breach_date,
        "discovery_date": discovery_date,
        "current_risk_score": risk_score,
        "risk_level": event.get("risk_level") or _risk_level_from_score(risk_score),
        "time_to_discovery": 0 if time_to_discovery is None else time_to_discovery,
        "data_exposed": event.get("data_exposed") or "",
    }
    return normalized


def _build_fallback_timeline_data(investigation_email: str = "") -> List[Dict[str, Any]]:
    """
    Build realistic simulated timeline entries when DB has no breaches.
    Timeline spans the last ~3 weeks with varied risk levels and scores.
    """
    today = date.today()
    suffix = investigation_email.split("@")[0] if investigation_email else "user"

    fallback_seed = [
        (24, "Credential Stuffing Attempt", 32, "Email addresses, Usernames"),
        (20, "Third-Party Vendor Leak", 48, "Email addresses, Phone numbers"),
        (16, "Forum Archive Exposure", 58, "Email addresses, Password hints"),
        (12, "Marketplace Data Leak", 72, "Email addresses, Phone numbers, Addresses"),
        (9, "Cloud Misconfiguration Dump", 84, "Passwords, IP addresses, Session tokens"),
        (6, "Payment Portal Incident", 91, "Financial Information, Full names, Phone numbers"),
    ]

    events: List[Dict[str, Any]] = []
    for offset, name, score, exposed in fallback_seed:
        breach_date = today - timedelta(days=offset)
        discovery_date = breach_date + timedelta(days=max(1, min(6, score // 20)))
        events.append(
            _normalize_timeline_event(
                {
                    "breach_name": f"{name} ({suffix})",
                    "breach_date": breach_date,
                    "discovery_date": discovery_date,
                    "current_risk_score": score,
                    "risk_level": _risk_level_from_score(score),
                    "time_to_discovery": (discovery_date - breach_date).days,
                    "data_exposed": exposed,
                }
            )
        )

    # Keep latest breach first to match existing UI behavior.
    events.sort(key=lambda row: row.get("breach_date") or date.min, reverse=True)
    return events


def _build_timeline_chart_data(timeline_data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """
    Aggregate timeline events by breach date for chart datasets.
    Returns labels, breach counts, and average risk scores.
    """
    buckets: Dict[str, Dict[str, float]] = {}
    for event in timeline_data:
        breach_date = event.get("breach_date")
        if isinstance(breach_date, (datetime, date)):
            label = breach_date.strftime("%Y-%m-%d")
        else:
            label = "Unknown"

        risk_score = event.get("current_risk_score", 50)
        try:
            risk_score = int(risk_score)
        except (TypeError, ValueError):
            risk_score = 50

        if label not in buckets:
            buckets[label] = {"count": 0, "risk_sum": 0}

        buckets[label]["count"] += 1
        buckets[label]["risk_sum"] += risk_score

    sorted_labels = sorted([key for key in buckets.keys() if key != "Unknown"])
    if "Unknown" in buckets:
        sorted_labels.append("Unknown")

    labels: List[str] = []
    breach_counts: List[int] = []
    avg_risk_scores: List[int] = []
    for label in sorted_labels:
        entry = buckets[label]
        labels.append(label)
        breach_counts.append(int(entry["count"]))
        avg_risk_scores.append(int(round(entry["risk_sum"] / max(1, entry["count"]))))

    return {
        "labels": labels,
        "breach_counts": breach_counts,
        "avg_risk_scores": avg_risk_scores,
    }


def _build_mitigation_dashboard_context(
    user_id: int,
    selected_investigation_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build context for mitigation dashboard using latest or selected investigation.
    Falls back to secure best-practice recommendations when no findings exist.
    """
    investigation: Optional[Dict[str, Any]] = None
    breach_rows: List[Dict[str, Any]] = []
    affected_data_types: List[str] = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                if selected_investigation_id:
                    cursor.execute(
                        """
                        SELECT id, email, phone_number, breach_count, risk_score, risk_level, checked_at
                        FROM investigation_logs
                        WHERE id = %s AND user_id = %s
                        LIMIT 1
                        """,
                        (selected_investigation_id, user_id),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, email, phone_number, breach_count, risk_score, risk_level, checked_at
                        FROM investigation_logs
                        WHERE user_id = %s
                        ORDER BY checked_at DESC
                        LIMIT 1
                        """,
                        (user_id,),
                    )

                investigation = cursor.fetchone()

                if investigation:
                    cursor.execute(
                        """
                        SELECT breach_name, breach_date, data_exposed
                        FROM breach_results
                        WHERE investigation_id = %s
                        ORDER BY breach_date DESC, id DESC
                        """,
                        (investigation["id"],),
                    )
                    breach_rows = cursor.fetchall()
    except MySQLError as e:
        print(f"Error building mitigation context: {e}")

    for row in breach_rows:
        data_exposed = row.get("data_exposed") or ""
        for token in data_exposed.split(","):
            token = token.strip()
            if token and token not in affected_data_types:
                affected_data_types.append(token)

    has_findings = bool(investigation and (investigation.get("breach_count") or 0) > 0)
    risk_score = int((investigation or {}).get("risk_score") or 0)
    risk_level = ((investigation or {}).get("risk_level") or _risk_level_from_score(risk_score)).upper()

    recommendations = {
        "critical_actions": [],
        "important_actions": [],
        "risk_summary": "",
        "estimated_total_time": "0 minutes",
    }

    if has_findings:
        recommendations = get_smart_recommendations(
            exposed_data_types=affected_data_types or ["Email"],
            risk_level=risk_level,
        )

    def _action_icon(action_type: str, priority_label: str) -> str:
        if "password" in action_type.lower():
            return "fa-key"
        if "monitor" in action_type.lower() or "alert" in action_type.lower():
            return "fa-bell"
        if "identity" in action_type.lower() or "fraud" in action_type.lower():
            return "fa-id-card"
        if priority_label == "Critical":
            return "fa-triangle-exclamation"
        if priority_label == "High":
            return "fa-shield-halved"
        return "fa-circle-check"

    def _normalize_actions(items: List[Dict[str, Any]], priority_label: str) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for item in items:
            action_type = item.get("action_type") or "Account Protection"
            normalized.append(
                {
                    "title": item.get("title") or action_type,
                    "description": item.get("description") or "Recommended security mitigation step.",
                    "priority_label": priority_label,
                    "icon": _action_icon(action_type, priority_label),
                    "time": item.get("estimated_time") or "15 minutes",
                }
            )
        return normalized

    critical_actions = _normalize_actions(recommendations.get("critical_actions", []), "Critical")
    high_actions = _normalize_actions(recommendations.get("important_actions", []), "High")

    medium_low_actions: List[Dict[str, Any]] = []
    for tip in get_mitigation_tips("High" if risk_level == "HIGH" else "Medium", has_findings):
        medium_low_actions.append(
            {
                "title": tip,
                "description": "Best-practice hardening recommendation.",
                "priority_label": "Medium" if has_findings else "Low",
                "icon": "fa-shield",
                "time": "10 minutes",
            }
        )

    if not has_findings:
        critical_actions = []
        high_actions = []
        medium_low_actions = [
            {
                "title": "Enable multi-factor authentication for important accounts",
                "description": "Adds a strong additional defense against account takeover.",
                "priority_label": "Low",
                "icon": "fa-mobile-screen-button",
                "time": "15 minutes",
            },
            {
                "title": "Use unique passwords with a password manager",
                "description": "Prevents credential reuse across breached websites.",
                "priority_label": "Low",
                "icon": "fa-key",
                "time": "20 minutes",
            },
            {
                "title": "Continue periodic dark web monitoring",
                "description": "Early detection lowers exposure impact significantly.",
                "priority_label": "Low",
                "icon": "fa-magnifying-glass",
                "time": "Ongoing",
            },
        ]

    suggested_tools = [
        {
            "name": "Password Manager",
            "description": "Generate and store unique high-entropy passwords.",
            "icon": "fa-key",
        },
        {
            "name": "MFA Authenticator App",
            "description": "Adds a second factor for account logins.",
            "icon": "fa-mobile-screen",
        },
        {
            "name": "Breach Monitoring Alerts",
            "description": "Receive alerts when your data appears in new leaks.",
            "icon": "fa-bell",
        },
        {
            "name": "Credit Monitoring",
            "description": "Track suspicious financial activity and identity fraud.",
            "icon": "fa-chart-line",
        },
    ]

    # Lower current risk translates into higher security posture score.
    security_improvement_score = max(5, min(100, 100 - risk_score))

    return {
        "investigation": investigation,
        "has_findings": has_findings,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_summary_text": recommendations.get("risk_summary") or "System posture looks stable.",
        "estimated_total_time": recommendations.get("estimated_total_time") or "0 minutes",
        "critical_actions": critical_actions,
        "high_actions": high_actions,
        "medium_low_actions": medium_low_actions,
        "affected_data_types": affected_data_types,
        "suggested_tools": suggested_tools,
        "security_improvement_score": security_improvement_score,
        "selected_investigation_id": selected_investigation_id,
    }


def get_mitigation_tips(risk_level: str, has_breach: bool) -> List[str]:
    """
    Return 3 security tips based on breach and risk outcome.
    """
    if not has_breach:
        return [
            "Continue using unique passwords for each account.",
            "Enable two-factor authentication (2FA) on important services.",
            "Monitor your email accounts periodically for suspicious activity.",
        ]

    if risk_level == "High":
        return [
            "Change passwords immediately, prioritizing email, banking, and social accounts.",
            "Enable two-factor authentication (2FA) on all accounts that support it.",
            "Review account activity and financial statements for unauthorized transactions.",
        ]

    if risk_level == "Low":
        return [
            "Be alert for phishing emails that reference leaked account details.",
            "Use an email alias strategy for non-critical sign-ups.",
            "Keep your recovery email and phone number up to date.",
        ]

    return [
        "Rotate credentials for key accounts and avoid password reuse.",
        "Enable two-factor authentication (2FA) where possible.",
        "Watch for targeted phishing attempts using exposed personal information.",
    ]


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """
    Main dashboard page:
    - GET: show empty search form.
    - POST: submit email, query HIBP, compute risk and recommendations.
    """
    # Load decoy bank breaches data for dashboard display
    decoy_bank_breaches = get_decoy_bank_breaches(limit=8)
    decoy_breaches_summary = get_decoy_breaches_summary()
    
    context = {
        "email": "",
        "phone_number": "",
        "bank_account": "",
        "breaches": [],
        "has_breach": False,
        "risk_level": None,
        "risk_score": 0,
        "tips": [],
        "message": None,
        "error": None,
        "db_warning": None,
        "phone_analysis": None,
        "phone_exposed": False,
        "bank_analysis": None,
        "telegram_status": None,
        "telegram_ok": False,
        "total_breaches": 0,
        "mock_mode": is_mock_mode_enabled(),
        "api_mode": "auto",
        "effective_data_mode": "Mock" if is_mock_mode_enabled() else "Live",
        "mock_emails": list(MOCK_BREACH_DATA.keys()),
        "mock_phone_numbers": list(MOCK_PHONE_BREACH_DATA.keys()),
        "mock_bank_accounts": MOCK_BANK_ACCOUNT_SAMPLES,
        "is_telegram_configured": is_telegram_configured(),
        "is_admin": session.get("is_admin", False),
        "is_authenticated": 'user_id' in session,
        "current_username": session.get("username"),
        "mitigation_data": [],
        "malaysian_resources": [],
        "estimated_mitigation_time": "0 minutes",
        "decoy_bank_breaches": decoy_bank_breaches,
        "decoy_breaches_summary": decoy_breaches_summary,
    }

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        bank_account = request.form.get("bank_account", "").strip()
        api_mode = resolve_api_mode(request.form.get("api_mode", "auto"))
        submit_action = request.form.get("submit_action", "analyze").strip().lower()
        context["email"] = email
        context["phone_number"] = phone_number
        context["bank_account"] = bank_account
        context["api_mode"] = api_mode

        use_mock = should_use_mock_data(api_mode)
        context["mock_mode"] = use_mock
        context["effective_data_mode"] = "Mock" if use_mock else "Live"

        bank_analysis = analyze_bank_account(bank_account)
        context["bank_analysis"] = bank_analysis

        if bank_account and not bank_analysis["is_valid"]:
            context["error"] = "Bank account format is invalid. Use 10 to 16 digits."
            return render_template("index.html", **context)

        if submit_action == "telegram_test":
            telegram_result = send_telegram_test_alert(
                email=email,
                phone_number=phone_number,
                data_mode=context["effective_data_mode"],
                bank_result=bank_analysis,
            )
            context["telegram_ok"] = telegram_result["ok"]
            context["telegram_status"] = telegram_result["message"]
            if telegram_result["ok"]:
                context["message"] = "Telegram test message sent. Check your Telegram app."
            return render_template("index.html", **context)

        if not email and not phone_number and not bank_account:
            context["error"] = "Please enter email, phone number, or bank account for demo check."
            return render_template("index.html", **context)

        phone_analysis = analyze_phone_number(phone_number)
        context["phone_analysis"] = phone_analysis

        if phone_number and not phone_analysis["is_valid"]:
            context["error"] = (
                "Phone number format is invalid. Use international format like +60123456789."
            )
            return render_template("index.html", **context)

        if not use_mock and API_KEY == "YOUR_HIBP_API_KEY_HERE":
            context["error"] = (
                "Live API mode selected but HIBP API key is missing. "
                "Set HIBP_API_KEY or switch to Mock mode."
            )
            return render_template("index.html", **context)

        try:
            lookup_result = check_email_logic(
                email=email,
                phone_number=phone_analysis["normalized"] or phone_number,
                use_mock=use_mock,
            )
        except requests.HTTPError as exc:
            context["error"] = (
                f"HIBP request failed with status {exc.response.status_code}. "
                "Please check API key, rate limits, or try again later."
            )
            return render_template("index.html", **context)
        except requests.RequestException:
            context["error"] = "Network error while contacting HIBP API."
            return render_template("index.html", **context)

        breaches = lookup_result["breaches"]
        context["phone_exposed"] = lookup_result["phone_exposed"]
        if lookup_result.get("phone_exposed") and lookup_result.get("phone_exposed_sources"):
            source_names = ", ".join(
                source["source"] for source in lookup_result["phone_exposed_sources"]
            )
            context["message"] = f"Phone Exposed: Yes (Source: {source_names})"
        elif lookup_result.get("message"):
            context["message"] = lookup_result["message"]

        risk_score = lookup_result["risk_score"]
        risk_level = lookup_result["risk_level"]

        context["risk_score"] = risk_score
        context["risk_level"] = risk_level
        context["total_breaches"] = len(breaches)

        if not breaches:
            if not context["message"]:
                context["message"] = "Your data is safe. No known breach found for this investigation."
            context["tips"] = get_mitigation_tips(risk_level="Low", has_breach=False)

            try:
                investigation_id = save_investigation(
                    email=email,
                    phone_number=phone_analysis["normalized"] or phone_number,
                    breaches=breaches,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    user_id=session.get('user_id'),
                )

                sensitive_data = has_sensitive_data_exposure(breaches)
                explanation = generate_risk_explanation(
                    risk_score=risk_score,
                    risk_level=risk_level,
                    breach_count=len(breaches),
                    sensitive_data=sensitive_data,
                )
                save_risk_score(
                    investigation_id=investigation_id,
                    breach_count=len(breaches),
                    sensitive_data=sensitive_data,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    explanation=explanation,
                )

                if risk_score >= 70 and not has_alert_for_investigation(
                    investigation_id, "telegram_auto_high_risk"
                ):
                    alert_result = send_telegram_alert(
                        email=email,
                        risk_score=risk_score,
                        risk_level=risk_level,
                        breach_count=len(breaches),
                    )
                    log_alert(
                        investigation_id=investigation_id,
                        alert_type="telegram_auto_high_risk",
                        message=alert_result["message"],
                        status="sent" if alert_result["ok"] else "failed",
                    )
                    if alert_result["ok"]:
                        context["telegram_ok"] = True
                        context["telegram_status"] = alert_result["message"]
                    else:
                        context["telegram_ok"] = False
                        context["telegram_status"] = alert_result["message"]
            except MySQLError:
                context["db_warning"] = (
                    "MySQL logging failed. Check DB credentials or server status in environment variables."
                )

            return render_template("index.html", **context)

        # Build a concise, dashboard-friendly breach list.
        formatted = []
        overall_risk = "Low"

        for breach in breaches:
            breach_name = breach.get("Name", "Unknown")
            breach_date = breach.get("BreachDate", "Unknown")
            data_classes = breach.get("DataClasses", [])

            current_risk = calculate_risk(data_classes)

            # Escalate overall risk if any breach is higher risk.
            if current_risk == "High":
                overall_risk = "High"
            elif current_risk == "Medium" and overall_risk != "High":
                overall_risk = "Medium"

            formatted.append(
                {
                    "name": breach_name,
                    "date": breach_date,
                    "data_classes": data_classes,
                    "risk": current_risk,
                }
            )

        context.update(
            {
                "breaches": formatted,
                "has_breach": True,
                "risk_level": risk_level,
                "tips": get_mitigation_tips(risk_level=overall_risk, has_breach=True),
            }
        )

        # Fetch mitigation recommendations and Malaysian resources
        try:
            # Extract all exposed data types from breaches
            exposed_data_types = []
            for breach in breaches:
                data_classes = breach.get("DataClasses", [])
                exposed_data_types.extend(data_classes)
            
            # Get smart recommendations
            recommendations = get_smart_recommendations(
                exposed_data_types=list(set(exposed_data_types)) or ["Email"],
                risk_level=overall_risk
            )
            
            # Format mitigation data for display
            formatted_mitigations = []
            if recommendations.get("critical_actions"):
                for action in recommendations["critical_actions"]:
                    formatted_mitigations.append(format_mitigation_for_display(action))
            
            if recommendations.get("important_actions"):
                for action in recommendations["important_actions"]:
                    formatted_mitigations.append(format_mitigation_for_display(action))
            
            # Get Malaysian resources
            malaysian_resources = get_malaysian_resources()
            
            context.update(
                {
                    "mitigation_data": formatted_mitigations,
                    "malaysian_resources": malaysian_resources,
                    "estimated_mitigation_time": calculate_total_time(
                        recommendations.get("critical_actions", []) + recommendations.get("important_actions", [])
                    ),
                }
            )
        except Exception as e:
            print(f"Error fetching mitigation data: {e}")
            # Continue without mitigation data if there's an error
            context["db_warning"] = (
                "Could not load mitigation recommendations. Check database connection."
            )

        try:
            investigation_id = save_investigation(
                email=email,
                phone_number=phone_analysis["normalized"] or phone_number,
                breaches=breaches,
                risk_score=risk_score,
                risk_level=risk_level,
                user_id=session.get('user_id'),
            )

            sensitive_data = has_sensitive_data_exposure(breaches)
            explanation = generate_risk_explanation(
                risk_score=risk_score,
                risk_level=risk_level,
                breach_count=len(breaches),
                sensitive_data=sensitive_data,
            )
            save_risk_score(
                investigation_id=investigation_id,
                breach_count=len(breaches),
                sensitive_data=sensitive_data,
                risk_score=risk_score,
                risk_level=risk_level,
                explanation=explanation,
            )

            if risk_score >= 70 and not has_alert_for_investigation(
                investigation_id, "telegram_auto_high_risk"
            ):
                alert_result = send_telegram_alert(
                    email=email,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    breach_count=len(breaches),
                )
                log_alert(
                    investigation_id=investigation_id,
                    alert_type="telegram_auto_high_risk",
                    message=alert_result["message"],
                    status="sent" if alert_result["ok"] else "failed",
                )
                if alert_result["ok"]:
                    context["telegram_ok"] = True
                    context["telegram_status"] = alert_result["message"]
                else:
                    context["telegram_ok"] = False
                    context["telegram_status"] = alert_result["message"]
        except MySQLError:
            context["db_warning"] = (
                "MySQL logging failed. Check DB credentials or server status in environment variables."
            )

    return render_template("index.html", **context)


@app.route("/signup", methods=["GET", "POST"])
def signup() -> str:
    """
    User registration route.
    GET: Show signup form
    POST: Create new user account
    """
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        # Validate password confirmation
        if password != password_confirm:
            error = "Passwords do not match."
            return render_template("signup.html", error=error, username=username, email=email)

        # Create user using auth module
        success_flag, message, user_id = create_user(
            username=username,
            email=email,
            password=password,
            role="user"
        )

        if success_flag:
            # Log signup activity
            try:
                log_user_activity(username=username, role="user", action="signup")
            except MySQLError:
                pass

            # Redirect to login with success message
            return redirect(url_for("login", signup_success="1"))
        else:
            error = message

    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    """
    User login route.
    GET: Show login form
    POST: Authenticate user and create session
    """
    error = None
    signup_success = request.args.get("signup_success")

    if request.method == "POST":
        email_or_username = request.form.get("email_or_username", "").strip()
        password = request.form.get("password", "")

        # Attempt login using auth module
        success, message, user_data = login_user(email_or_username, password)

        if success:
            # Create session
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['email'] = user_data['email']
            session['role'] = user_data['role']
            session.permanent = True

            # Log login activity
            try:
                log_user_activity(
                    username=user_data['username'],
                    role=user_data['role'],
                    action="login"
                )
            except MySQLError:
                pass

            # Redirect to dashboard
            return redirect(url_for("index"))
        else:
            error = message
            # Log failed login attempt
            try:
                log_user_activity(
                    username=email_or_username or "unknown",
                    role="guest",
                    action="failed_login"
                )
            except MySQLError:
                pass

    return render_template(
        "login.html",
        error=error,
        signup_success=signup_success
    )


@app.route("/logout")
def logout():
    """
    User logout route.
    Clears session and redirects to home.
    """
    username = session.get("username") or "unknown"
    role = session.get("role") or "user"

    try:
        log_user_activity(username=username, role=role, action="logout")
    except MySQLError:
        pass

    session.clear()
    return redirect(url_for("index"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login() -> str:
    """
    Simple admin login to protect investigation history.
    DEPRECATED: Use /login for user authentication instead.
    Kept for backward compatibility during transition.
    """
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            session["admin_username"] = username
            session["admin_role"] = "admin"
            try:
                log_user_activity(username=username, role="admin", action="login")
            except MySQLError:
                pass
            return redirect(url_for("history"))

        try:
            log_user_activity(
                username=username or "unknown",
                role="guest",
                action="failed_login",
            )
        except MySQLError:
            pass

        error = "Invalid admin credentials."

    return render_template("login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    """
    DEPRECATED: Use /logout instead.
    Legacy route kept for backward compatibility.
    """
    username = session.get("admin_username") or "unknown"
    role = session.get("admin_role") or ("admin" if session.get("is_admin") else "guest")

    try:
        log_user_activity(username=username, role=role, action="logout")
    except MySQLError:
        pass

    session.pop("is_admin", None)
    session.pop("admin_username", None)
    session.pop("admin_role", None)
    return redirect(url_for("index"))


@app.route("/history")
def history() -> str:
    """
    Investigation history view with optional date/risk filters.
    Requires authentication (user login or admin login).
    Regular users see only their own investigations.
    Admins see all investigations.
    """
    # Check authentication: either new user session OR old admin session
    is_user_authenticated = 'user_id' in session
    is_admin_authenticated = session.get("is_admin")

    if not (is_user_authenticated or is_admin_authenticated):
        return redirect(url_for("login"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    risk_level = request.args.get("risk_level", "").strip().upper()

    rows: List[Dict[str, Any]] = []
    error = None

    try:
        # For regular users, filter by their user_id
        # For admins, show all investigations
        if is_user_authenticated:
            rows = fetch_investigation_history(
                start_date, end_date, risk_level,
                user_id=session.get('user_id')
            )
        else:
            # Admin view: show all
            rows = fetch_investigation_history(start_date, end_date, risk_level)
    except MySQLError:
        error = "Unable to load investigation history. Please verify MySQL connection."

    return render_template(
        "history.html",
        rows=rows,
        start_date=start_date,
        end_date=end_date,
        risk_level=risk_level,
        error=error,
        is_admin=is_admin_authenticated,
    )


@app.route("/history/export")
def export_history_csv():
    """
    Export filtered investigation history as CSV for FYP evidence.
    Requires authentication; regular users export only their data.
    """
    # Check authentication
    is_user_authenticated = 'user_id' in session
    is_admin_authenticated = session.get("is_admin")

    if not (is_user_authenticated or is_admin_authenticated):
        return redirect(url_for("login"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    risk_level = request.args.get("risk_level", "").strip().upper()

    try:
        # For regular users, export only their data
        if is_user_authenticated:
            rows = fetch_investigation_history(
                start_date, end_date, risk_level,
                user_id=session.get('user_id')
            )
        else:
            rows = fetch_investigation_history(start_date, end_date, risk_level)
    except MySQLError:
        return Response(
            "Unable to export CSV. Please verify MySQL connection.",
            status=500,
            mimetype="text/plain",
        )

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "email",
            "phone_number",
            "breach_count",
            "risk_score",
            "risk_level",
            "checked_at",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row.get("id"),
                row.get("email"),
                row.get("phone_number"),
                row.get("breach_count"),
                row.get("risk_score"),
                row.get("risk_level"),
                row.get("checked_at"),
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=investigation_history.csv"},
    )


# ============================================================================
# FEATURE 1: Real-Time Monitoring + Breach Timeline Routes
# ============================================================================

@app.route("/monitoring", methods=["GET"])
@login_required
def monitoring_dashboard():
    """
    Monitoring dashboard - View active monitoring and timeline
    """
    user_id = session.get('user_id')
    
    # Get user's active monitoring
    monitoring_list = get_user_monitoring(user_id)
    
    # Get timeline statistics
    timeline_stats = get_timeline_statistics(user_id)
    
    return render_template(
        "monitoring_dashboard.html",
        monitoring_list=monitoring_list,
        timeline_stats=timeline_stats,
        tr=tr
    )


@app.route("/monitoring/subscribe", methods=["POST"])
@login_required
def subscribe_monitoring():
    """
    Subscribe email/phone to automatic monitoring
    """
    user_id = session.get('user_id')
    
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    frequency = request.form.get('frequency', 'weekly')
    
    if not email:
        return {"success": False, "message": "Email is required"}, 400
    
    success, message = create_monitoring_subscription(
        user_id=user_id,
        email=email,
        phone_number=phone or None,
        check_frequency=frequency
    )
    
    if success:
        return {"success": True, "message": message}, 200
    else:
        return {"success": False, "message": message}, 400


@app.route("/war-room", methods=["GET"])
@app.route("/war-room/", methods=["GET"])
@login_required
def war_room_dashboard():
    """
    SOC War Room dashboard:
    - Live risk trend
    - Incident ticker
    - Dark web alert stream
    - Mitigation action queue
    """
    user_id = session.get("user_id")
    refresh_seconds = request.args.get("refresh", default=30, type=int) or 30
    refresh_seconds = max(10, min(300, refresh_seconds))

    stats = {
        "total_investigations": 0,
        "avg_risk_score": 0,
        "critical_cases": 0,
    }
    recent_investigations: List[Dict[str, Any]] = []
    risk_trend_rows: List[Dict[str, Any]] = []
    timeline_events: List[Dict[str, Any]] = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total_investigations,
                        COALESCE(ROUND(AVG(risk_score)), 0) AS avg_risk_score,
                        SUM(CASE WHEN risk_score >= 80 OR risk_level = 'HIGH' THEN 1 ELSE 0 END) AS critical_cases
                    FROM investigation_logs
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                stats_row = cursor.fetchone() or {}
                stats = {
                    "total_investigations": int(stats_row.get("total_investigations") or 0),
                    "avg_risk_score": int(stats_row.get("avg_risk_score") or 0),
                    "critical_cases": int(stats_row.get("critical_cases") or 0),
                }

                cursor.execute(
                    """
                    SELECT id, email, phone_number, breach_count, risk_score, risk_level, checked_at
                    FROM investigation_logs
                    WHERE user_id = %s
                    ORDER BY checked_at DESC
                    LIMIT 15
                    """,
                    (user_id,),
                )
                recent_investigations = cursor.fetchall() or []

                cursor.execute(
                    """
                    SELECT id, risk_score, breach_count, checked_at
                    FROM investigation_logs
                    WHERE user_id = %s
                    ORDER BY checked_at DESC
                    LIMIT 12
                    """,
                    (user_id,),
                )
                risk_trend_rows = cursor.fetchall() or []

                cursor.execute(
                    """
                    SELECT
                        br.investigation_id,
                        br.breach_name,
                        br.breach_date,
                        br.data_exposed,
                        il.risk_score,
                        il.risk_level,
                        il.checked_at,
                        il.email
                    FROM breach_results br
                    INNER JOIN investigation_logs il ON br.investigation_id = il.id
                    WHERE il.user_id = %s
                    ORDER BY COALESCE(br.breach_date, DATE(il.checked_at)) DESC, br.id DESC
                    LIMIT 20
                    """,
                    (user_id,),
                )
                timeline_events = cursor.fetchall() or []
    except MySQLError as e:
        print(f"Error building war room dashboard: {e}")

    darkweb_alerts = get_darkweb_findings(user_id, unresolved_only=True)[:12]

    risk_trend_labels: List[str] = []
    risk_trend_scores: List[int] = []
    risk_trend_breaches: List[int] = []
    for item in reversed(risk_trend_rows):
        checked_at = item.get("checked_at")
        if isinstance(checked_at, (datetime, date)):
            label = checked_at.strftime("%m-%d %H:%M")
        else:
            label = str(checked_at or "-")
        risk_trend_labels.append(label)
        risk_trend_scores.append(int(item.get("risk_score") or 0))
        risk_trend_breaches.append(int(item.get("breach_count") or 0))

    mitigation_queue: List[Dict[str, Any]] = []
    for item in recent_investigations:
        risk_score = int(item.get("risk_score") or 0)
        breach_count = int(item.get("breach_count") or 0)
        if risk_score < 40 and breach_count == 0:
            continue

        risk_level = str(item.get("risk_level") or _risk_level_from_score(risk_score)).upper()
        tips = get_mitigation_tips(risk_level.title(), breach_count > 0)
        mitigation_queue.append(
            {
                "investigation_id": item.get("id"),
                "email": item.get("email") or "Unknown",
                "risk_score": risk_score,
                "risk_level": risk_level,
                "breach_count": breach_count,
                "top_action": tips[0] if tips else "Review account security posture.",
            }
        )
        if len(mitigation_queue) >= 8:
            break

    incident_ticker: List[Dict[str, Any]] = []
    for alert in darkweb_alerts[:6]:
        incident_ticker.append(
            {
                "severity": alert.get("severity") or "MEDIUM",
                "text": f"Dark web alert on {alert.get('found_on_platform', 'Unknown source')}: {alert.get('snippet', 'New exposure signal')}",
                "time": alert.get("first_detected") or alert.get("created_at") or "Recent",
            }
        )

    for event in timeline_events[:8]:
        event_risk = int(event.get("risk_score") or 0)
        incident_ticker.append(
            {
                "severity": "HIGH" if event_risk >= 75 else ("MEDIUM" if event_risk >= 40 else "LOW"),
                "text": f"Timeline event: {event.get('breach_name', 'Unknown breach')} linked to case #{event.get('investigation_id')}",
                "time": event.get("breach_date") or event.get("checked_at") or "Recent",
            }
        )

    incident_ticker = incident_ticker[:20]

    return render_template(
        "war_room.html",
        stats=stats,
        recent_investigations=recent_investigations,
        timeline_events=timeline_events,
        darkweb_alerts=darkweb_alerts,
        mitigation_queue=mitigation_queue,
        incident_ticker=incident_ticker,
        risk_trend_labels=risk_trend_labels,
        risk_trend_scores=risk_trend_scores,
        risk_trend_breaches=risk_trend_breaches,
        refresh_seconds=refresh_seconds,
        tr=tr,
    )


@app.route("/timeline/<int:investigation_id>", methods=["GET"])
@login_required
def view_breach_timeline(investigation_id: int):
    """
    View breach timeline for an investigation
    Shows when breaches occurred vs when discovered
    Transforms breach results into timeline format for visualization
    """
    user_id = session.get('user_id')
    
    # Verify ownership and get investigation
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM investigation_logs WHERE id = %s AND user_id = %s",
            (investigation_id, user_id)
        )
        investigation = cursor.fetchone()
        
        if not investigation:
            cursor.close()
            conn.close()
            return "Not found", 404
        
        # Fetch breach results for this investigation
        cursor.execute(
            """SELECT 
                id, breach_name, breach_date, data_exposed 
               FROM breach_results 
               WHERE investigation_id = %s 
               ORDER BY breach_date DESC, id DESC""",
            (investigation_id,)
        )
        breach_results = cursor.fetchall()
        cursor.close()
        conn.close()
        
    except MySQLError as e:
        print(f"Error fetching breach data: {e}")
        return "Database error", 500
    
    # Get timeline data from the more comprehensive function in monitoring.py
    real_timeline_data = get_breach_timeline(investigation_id) or []
    timeline_has_real_data = len(real_timeline_data) > 0

    if timeline_has_real_data:
        timeline_data = [_normalize_timeline_event(event) for event in real_timeline_data]
    else:
        timeline_data = _build_fallback_timeline_data(investigation.get("email") or "")
    
    # Get timeline statistics for KPI cards
    timeline_stats = get_timeline_statistics(user_id)

    # Build chart + table data from whichever timeline set is active.
    timeline_chart_data = _build_timeline_chart_data(timeline_data)

    # Attach breaches to investigation object for template compatibility
    investigation['breaches'] = breach_results
    
    return render_template(
        "breach_timeline.html",
        investigation=investigation,
        timeline_data=timeline_data,
        timeline_stats=timeline_stats,
        timeline_has_real_data=timeline_has_real_data,
        timeline_chart_data=timeline_chart_data,
        tr=tr
    )


@app.route("/mitigation", methods=["GET"])
@login_required
def mitigation():
    """
    Mitigation dashboard entry route.
    Uses latest investigation by default, or accepts ?investigation_id=<id>.
    """
    user_id = session.get("user_id")
    investigation_id = request.args.get("investigation_id", type=int)

    context = _build_mitigation_dashboard_context(
        user_id=user_id,
        selected_investigation_id=investigation_id,
    )
    context["tr"] = tr
    return render_template("mitigation.html", **context)


@app.route("/mitigation/<int:investigation_id>", methods=["GET"])
@login_required
def mitigation_planning(investigation_id: int):
    """
    Show mitigation planning for an investigation
    Displays AI-generated or rule-based mitigation actions
    """
    user_id = session.get("user_id")

    context = _build_mitigation_dashboard_context(
        user_id=user_id,
        selected_investigation_id=investigation_id,
    )

    if not context.get("investigation"):
        return "Not found", 404

    actions: List[Dict[str, Any]] = []
    for group_name, priority in (
        ("critical_actions", "Critical"),
        ("high_actions", "High"),
        ("medium_low_actions", "Medium/Low"),
    ):
        for item in context.get(group_name, []) or []:
            actions.append(
                {
                    "title": item.get("title") or "Security action",
                    "description": item.get("description") or "Recommended mitigation step.",
                    "icon": item.get("icon") or "fa-shield-halved",
                    "priority": item.get("priority_label") or priority,
                    "time": item.get("time") or "15 minutes",
                }
            )

    security_improvements = [
        "Enable multi-factor authentication (MFA) for high-value accounts.",
        "Use unique passwords with a trusted password manager.",
        "Enable account breach alerts and monitor suspicious sign-ins.",
        "Review recovery email/phone settings and remove unknown devices.",
    ]

    context.update(
        {
            "risk_score": context.get("risk_score", 0),
            "risk_level": context.get("risk_level", "LOW"),
            "actions": actions,
            "security_improvements": security_improvements,
            "has_actions": bool(actions),
            "tr": tr,
        }
    )

    return render_template("mitigation_response.html", **context)


# ============================================================================
# FEATURE 2: Dark Web Monitoring Routes
# ============================================================================

@app.route("/darkweb/check/<int:investigation_id>", methods=["GET", "POST"])
@login_required
def darkweb_check(investigation_id: int):
    """
    Check if email from investigation appears on dark web
    """
    user_id = session.get('user_id')
    
    # Verify ownership
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT email FROM investigation_logs WHERE id = %s AND user_id = %s",
            (investigation_id, user_id)
        )
        investigation = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not investigation:
            return "Not found", 404
    except MySQLError:
        return "Database error", 500
    
    if request.method == "POST":
        email = investigation['email']
        
        # Check dark web (mock for now)
        findings = check_darkweb_mock(email)
        
        # Record findings
        if findings:
            for finding in findings:
                record_darkweb_finding(
                    investigation_id=investigation_id,
                    user_id=user_id,
                    query_term=email,
                    platform=finding['platform'],
                    snippet=finding['snippet'],
                    severity=finding['severity'],
                    risk_reason=finding.get('risk_reason')
                )
        
        return render_template(
            "darkweb_results.html",
            email=email,
            findings=findings,
            has_findings=len(findings) > 0,
            tr=tr
        )
    
    # GET - Show findings
    findings = get_investigation_darkweb_findings(investigation_id)
    return render_template(
        "darkweb_dashboard.html",
        email=investigation['email'],
        findings=findings,
        tr=tr
    )


@app.route("/darkweb/findings", methods=["GET"])
@login_required
def darkweb_user_findings():
    """
    View all dark web findings for user
    """
    user_id = session.get('user_id')
    
    findings = get_darkweb_findings(user_id, unresolved_only=False)
    risk_summary = calculate_darkweb_risk_score(user_id)
    
    return render_template(
        "darkweb_findings_summary.html",
        findings=findings,
        risk_summary=risk_summary,
        tr=tr
    )


# ============================================================================
# FEATURE 3: Data Type Analysis + Hash Algorithm Routes
# ============================================================================

@app.route("/analysis/data-types/<int:investigation_id>", methods=["GET"])
@login_required
def analyze_data_types(investigation_id: int):
    """
    Analyze what data types were exposed in breaches
    """
    user_id = session.get('user_id')
    
    # Get investigation
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT il.id, il.email, il.risk_score, br.breach_name, br.data_exposed
            FROM investigation_logs il
            LEFT JOIN breach_results br ON il.id = br.investigation_id
            WHERE il.id = %s AND il.user_id = %s
        """, (investigation_id, user_id))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results:
            return "Not found", 404
        
        investigation = results[0]
        breaches = results
    except MySQLError:
        return "Database error", 500
    
    # Analyze data types for each breach
    analysis_results = []
    for breach in breaches:
        if breach['data_exposed']:
            analysis = analyze_breach_datatypes(
                investigation_id,
                breach['breach_name'],
                breach['data_exposed']
            )
            analysis_results.append({
                'breach_name': breach['breach_name'],
                'analysis': analysis
            })
    
    return render_template(
        "data_type_analysis.html",
        investigation=investigation,
        analysis_results=analysis_results,
        tr=tr
    )


@app.route("/analysis/hash-check/<int:investigation_id>", methods=["GET"])
@login_required
def hash_algorithm_check(investigation_id: int):
    """
    Analyze hash algorithms and password crackability
    """
    user_id = session.get('user_id')
    
    # Get investigation with breaches
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT il.id, il.email, il.risk_score, br.breach_name, br.data_exposed
            FROM investigation_logs il
            LEFT JOIN breach_results br ON il.id = br.investigation_id
            WHERE il.id = %s AND il.user_id = %s
        """, (investigation_id, user_id))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results:
            return "Not found", 404
        
        investigation = results[0]
        breaches = results
    except MySQLError:
        return "Database error", 500
    
    # Analyze hash algorithms
    forensic_reports = []
    for breach in breaches:
        if breach['data_exposed']:
            report = generate_forensic_report(
                investigation_id,
                breach['breach_name'],
                breach['data_exposed']
            )
            forensic_reports.append(report)
            
            # Store in database
            store_enhanced_breach_details(
                investigation_id,
                breach['breach_name'],
                report['data_types'],
                report['hash_algorithm'],
                report.get('hash_is_salted'),
                report.get('password_crack_risk', {}).get('crackability_level')
            )
    
    # Get reference data
    hash_reference = get_hash_algorithm_reference()
    datatype_reference = get_data_type_risk_reference()
    
    return render_template(
        "hash_analysis.html",
        investigation=investigation,
        forensic_reports=forensic_reports,
        hash_reference=hash_reference,
        datatype_reference=datatype_reference,
        tr=tr
    )


@app.route("/api/risk-matrix", methods=["GET"])
def api_risk_matrix():
    """
    API endpoint for data type risk matrix
    """
    matrix = get_data_type_risk_reference()
    return {
        "success": True,
        "data": matrix
    }, 200


@app.route("/api/hash-algorithms", methods=["GET"])
def api_hash_algorithms():
    """
    API endpoint for hash algorithm reference
    """
    algorithms = get_hash_algorithm_reference()
    return {
        "success": True,
        "data": algorithms
    }, 200


@app.route('/api/heatmap')
def heatmap_data():
    # Query dari geographic_heatmap_data
    # Return JSON [{lat: ..., lng: ..., value: ...}, ...]
    pass


# ============================================================================
# DECOY BANK BREACHES FUNCTIONS
# All data is FICTIONAL for academic demonstration only
# ============================================================================

def get_decoy_bank_breaches(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch decoy bank breach data from MySQL database.
    Returns list of bank breaches with risk indicators.
    
    Args:
        limit: Maximum number of records to fetch (default: 10)
        
    Returns:
        List of decoy breaches with all relevant details
    """
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        query = """
        SELECT 
            breach_id,
            institution_name,
            institution_type,
            country,
            breach_date,
            breach_type,
            severity_level,
            affected_accounts,
            exposed_data_types,
            breach_description,
            data_sample_masked
        FROM decoy_bank_breaches
        WHERE is_active = TRUE
        ORDER BY breach_date DESC, severity_level DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Transform results for template consumption
        breaches = []
        for breach in results:
            breaches.append({
                "breach_id": breach.get("breach_id", ""),
                "institution": breach.get("institution_name", "Unknown"),
                "type": breach.get("institution_type", "Bank"),
                "country": breach.get("country", "Malaysia"),
                "date": breach.get("breach_date", "").isoformat() if breach.get("breach_date") else "Unknown",
                "breach_type": breach.get("breach_type", "Unknown"),
                "severity": breach.get("severity_level", "Medium"),
                "affected": breach.get("affected_accounts", 0),
                "data_exposed": breach.get("exposed_data_types", ""),
                "description": breach.get("breach_description", ""),
                "sample": breach.get("data_sample_masked", "Not Available"),
            })
        
        return breaches
        
    except MySQLError as e:
        # Return empty list if DB connection fails
        return []


def get_decoy_breaches_by_severity() -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch decoy bank breaches grouped by severity level for dashboard display.
    Returns a dictionary with severity levels as keys and breach lists as values.
    """
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        query = """
        SELECT 
            severity_level,
            breach_id,
            institution_name,
            breach_date,
            affected_accounts,
            data_sample_masked
        FROM decoy_bank_breaches
        WHERE is_active = TRUE
        ORDER BY breach_date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Group by severity
        breaches_by_severity = {"High": [], "Medium": [], "Low": []}
        
        for breach in results:
            severity = breach.get("severity_level", "Medium")
            breaches_by_severity.setdefault(severity, []).append({
                "breach_id": breach.get("breach_id", ""),
                "institution": breach.get("institution_name", "Unknown"),
                "date": breach.get("breach_date", "").isoformat() if breach.get("breach_date") else "Unknown",
                "affected": breach.get("affected_accounts", 0),
                "sample": breach.get("data_sample_masked", ""),
            })
        
        return breaches_by_severity
        
    except MySQLError:
        return {"High": [], "Medium": [], "Low": []}


def get_decoy_breaches_summary() -> Dict[str, Any]:
    """
    Get summary statistics of decoy bank breaches for dashboard cards.
    """
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        
        # Get total count and affected accounts
        query = """
        SELECT 
            COUNT(*) as total_breaches,
            SUM(affected_accounts) as total_affected,
            COUNT(CASE WHEN severity_level = 'High' THEN 1 END) as high_severity,
            COUNT(CASE WHEN severity_level = 'Medium' THEN 1 END) as medium_severity,
            COUNT(CASE WHEN severity_level = 'Low' THEN 1 END) as low_severity,
            MIN(breach_date) as oldest_breach,
            MAX(breach_date) as latest_breach
        FROM decoy_bank_breaches
        WHERE is_active = TRUE
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        return {
            "total_breaches": result.get("total_breaches", 0) if result else 0,
            "total_affected_accounts": result.get("total_affected", 0) if result else 0,
            "high_severity_count": result.get("high_severity", 0) if result else 0,
            "medium_severity_count": result.get("medium_severity", 0) if result else 0,
            "low_severity_count": result.get("low_severity", 0) if result else 0,
            "oldest_breach": str(result.get("oldest_breach", "")) if result and result.get("oldest_breach") else "Unknown",
            "latest_breach": str(result.get("latest_breach", "")) if result and result.get("latest_breach") else "Unknown",
        }
        
    except MySQLError:
        return {
            "total_breaches": 0,
            "total_affected_accounts": 0,
            "high_severity_count": 0,
            "medium_severity_count": 0,
            "low_severity_count": 0,
            "oldest_breach": "Unknown",
            "latest_breach": "Unknown",
        }


@app.route("/decoy-breaches", methods=["GET"])
def get_decoy_breaches_api() -> tuple:
    """
    API endpoint to fetch decoy bank breach data in JSON format.
    Useful for AJAX/dynamic loading on the dashboard.
    """
    limit = request.args.get("limit", 15, type=int)
    limit = min(limit, 100)  # Cap at 100 to prevent abuse
    
    breaches = get_decoy_bank_breaches(limit=limit)
    summary = get_decoy_breaches_summary()
    
    return {
        "success": True,
        "summary": summary,
        "breaches": breaches,
        "note": "All data is FICTIONAL for academic demonstration only"
    }, 200


if __name__ == "__main__":
    # Debug=True is convenient for local FYP prototyping.
    try:
        init_db()
    except MySQLError:
        # App still runs for demo even if DB is unavailable, but logging is disabled.
        pass
    # Disable reloader to avoid duplicate process behavior in Windows/VS Code debugging.
    app.run(debug=True, use_reloader=False)
