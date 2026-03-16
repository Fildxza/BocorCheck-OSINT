import os
import csv
from io import StringIO
from datetime import date, datetime
from typing import List, Dict, Any, Optional

import phonenumbers
import requests
from flask import Flask, render_template, request, redirect, url_for, session, Response
from mysql.connector import Error as MySQLError
from mysql.connector import connect


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-for-production")

# Replace this with your real HIBP API key for local testing.
# Recommended: keep it in an environment variable instead of hardcoding.
API_KEY = os.getenv("HIBP_API_KEY", "YOUR_HIBP_API_KEY_HERE")
HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount"
REQUEST_TIMEOUT_SECONDS = 15
PHONE_DEFAULT_REGION = os.getenv("PHONE_DEFAULT_REGION", "MY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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

# Mock mode helps local demo when API key is not available yet.
# It can be forced via USE_MOCK_DATA=true in environment variables.
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Hardcoded prototype dataset for thesis demo.
# Includes user's requested university email for presentation use.
MOCK_BREACH_DATA: Dict[str, List[Dict[str, Any]]] = {
    "fildza@ur.unirazak.edu.my": [
        {
            "Name": "EduForumDemo",
            "BreachDate": "2024-02-11",
            "DataClasses": ["Email addresses", "Passwords"],
        }
    ],
    "amin.demo@gmail.com": [
        {
            "Name": "ShopLink",
            "BreachDate": "2023-08-03",
            "DataClasses": ["Email addresses", "Passwords"],
        },
        {
            "Name": "PayTrack",
            "BreachDate": "2022-05-15",
            "DataClasses": ["Email addresses", "Financial Information"],
        },
    ],
    "nur.safe@example.com": [],
    "hafiz.lowrisk@example.com": [
        {
            "Name": "NewsletterHub",
            "BreachDate": "2021-11-07",
            "DataClasses": ["Email addresses"],
        }
    ],
}

MOCK_PHONE_BREACH_DATA: Dict[str, List[Dict[str, Any]]] = {
    "+60123456789": [
        {
            "Name": "MobileMart",
            "BreachDate": "2024-07-20",
            "DataClasses": ["Phone numbers", "Email addresses"],
        }
    ],
    "+60135550011": [
        {
            "Name": "RewardsPortal",
            "BreachDate": "2020-02-14",
            "DataClasses": ["Phone numbers", "Passwords"],
        }
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


def query_mock_breaches(email: str) -> List[Dict[str, Any]]:
    """
    Return hardcoded breach records for demo emails.
    Unknown emails default to no breach for safe-message demonstration.
    """
    return MOCK_BREACH_DATA.get(email.lower(), [])


def query_mock_phone_breaches(phone_number: str) -> List[Dict[str, Any]]:
    """
    Return hardcoded breach records for demo phone numbers.
    """
    return MOCK_PHONE_BREACH_DATA.get(phone_number, [])


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
    Simple risk scoring logic for thesis prototype:
    - High: if leaked data includes passwords or financial data.
    - Low: if data only includes email addresses.
    - Medium: any other combination.
    """
    normalized = {item.strip().lower() for item in data_classes}

    has_password = "passwords" in normalized

    # HIBP commonly uses labels like "Financial Information".
    has_financial = any("financial" in item for item in normalized)

    if has_password or has_financial:
        return "High"

    if normalized == {"email addresses"}:
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


def get_db_connection():
    """
    Create MySQL connection from environment configuration.
    """
    config = {
        "host": os.getenv("MYSQL_HOST", MYSQL_DEFAULTS["host"]),
        "port": int(os.getenv("MYSQL_PORT", str(MYSQL_DEFAULTS["port"]))),
        "user": os.getenv("MYSQL_USER", MYSQL_DEFAULTS["user"]),
        "password": os.getenv("MYSQL_PASSWORD", MYSQL_DEFAULTS["password"]),
        "database": os.getenv("MYSQL_DATABASE", MYSQL_DEFAULTS["database"]),
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
        }
        return connect(**fallback)


def init_db() -> None:
    """
    Initialize required investigation tables.
    """
    create_investigation_logs = """
    CREATE TABLE IF NOT EXISTS investigation_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NULL,
        phone_number VARCHAR(32) NULL,
        breach_count INT NOT NULL,
        risk_score INT NOT NULL,
        risk_level VARCHAR(10) NOT NULL,
        checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """

    create_breach_results = """
    CREATE TABLE IF NOT EXISTS breach_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        investigation_id INT NOT NULL,
        breach_name VARCHAR(255) NOT NULL,
        breach_date DATE NULL,
        data_exposed TEXT,
        FOREIGN KEY (investigation_id) REFERENCES investigation_logs(id) ON DELETE CASCADE
    )
    """

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_investigation_logs)
            cursor.execute(create_breach_results)
        conn.commit()


def save_investigation(
    email: str,
    phone_number: str,
    breaches: List[Dict[str, Any]],
    risk_score: int,
    risk_level: str,
) -> None:
    """
    Persist one investigation summary and its breach details in MySQL.
    """
    insert_log = """
    INSERT INTO investigation_logs (email, phone_number, breach_count, risk_score, risk_level)
    VALUES (%s, %s, %s, %s, %s)
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


def fetch_investigation_history(
    start_date: str = "",
    end_date: str = "",
    risk_level: str = "",
) -> List[Dict[str, Any]]:
    """
    Get investigation logs with optional date and risk filters.
    """
    query = """
    SELECT id, email, phone_number, breach_count, risk_score, risk_level, checked_at
    FROM investigation_logs
    WHERE 1=1
    """
    params: List[Any] = []

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
        "is_admin": is_admin_logged_in(),
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

        breaches: List[Dict[str, Any]] = []
        if use_mock:
            if email:
                breaches.extend(query_mock_breaches(email=email))
            if phone_analysis["normalized"]:
                breaches.extend(query_mock_phone_breaches(phone_analysis["normalized"]))
        else:
            if API_KEY == "YOUR_HIBP_API_KEY_HERE":
                context["error"] = (
                    "Live API mode selected but HIBP API key is missing. "
                    "Set HIBP_API_KEY or switch to Mock mode."
                )
                return render_template("index.html", **context)

            if email:
                try:
                    breaches = query_hibp_breaches(email=email, api_key=API_KEY)
                except requests.HTTPError as exc:
                    context["error"] = (
                        f"HIBP request failed with status {exc.response.status_code}. "
                        "Please check API key, rate limits, or try again later."
                    )
                    return render_template("index.html", **context)
                except requests.RequestException:
                    context["error"] = "Network error while contacting HIBP API."
                    return render_template("index.html", **context)

            # HIBP account endpoint does not support direct phone-only search.
            if phone_number and not email:
                context["message"] = (
                    "Phone OSINT completed. Live breach lookup requires email input on HIBP v3 account endpoint."
                )

        # Deduplicate by breach name to avoid duplicate rows when email+phone produce same mock breach.
        unique: Dict[str, Dict[str, Any]] = {}
        for breach in breaches:
            unique[breach.get("Name", "Unknown")] = breach
        breaches = list(unique.values())

        phone_exposed = _contains_phone_exposure(breaches)
        context["phone_exposed"] = phone_exposed

        risk_result = calculate_risk_score(
            {"breaches": breaches, "phone_exposed": phone_exposed}
        )
        risk_score = risk_result["risk_score"]
        risk_level = risk_result["risk_level"]

        context["risk_score"] = risk_score
        context["risk_level"] = risk_level
        context["total_breaches"] = len(breaches)

        if not breaches:
            if not context["message"]:
                context["message"] = "Your data is safe. No known breach found for this investigation."
            context["tips"] = get_mitigation_tips(risk_level="Low", has_breach=False)

            try:
                save_investigation(
                    email=email,
                    phone_number=phone_analysis["normalized"] or phone_number,
                    breaches=breaches,
                    risk_score=risk_score,
                    risk_level=risk_level,
                )
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

        try:
            save_investigation(
                email=email,
                phone_number=phone_analysis["normalized"] or phone_number,
                breaches=breaches,
                risk_score=risk_score,
                risk_level=risk_level,
            )
        except MySQLError:
            context["db_warning"] = (
                "MySQL logging failed. Check DB credentials or server status in environment variables."
            )

    return render_template("index.html", **context)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login() -> str:
    """
    Simple admin login to protect investigation history.
    """
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("history"))

        error = "Invalid admin credentials."

    return render_template("login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/history")
def history() -> str:
    """
    Investigation history view with optional date/risk filters.
    """
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    risk_level = request.args.get("risk_level", "").strip().upper()

    rows: List[Dict[str, Any]] = []
    error = None
    try:
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
    )


@app.route("/history/export")
def export_history_csv():
    """
    Export filtered investigation history as CSV for FYP evidence.
    """
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    risk_level = request.args.get("risk_level", "").strip().upper()

    try:
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


if __name__ == "__main__":
    # Debug=True is convenient for local FYP prototyping.
    try:
        init_db()
    except MySQLError:
        # App still runs for demo even if DB is unavailable, but logging is disabled.
        pass
    app.run(debug=True)
