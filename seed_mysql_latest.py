import os
from typing import List, Tuple

from mysql.connector import Error as MySQLError
from mysql.connector import connect


MYSQL_DEFAULTS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "fyp_user",
    "password": "Admin123!",
    "database": "fyp_osint",
}


INVESTIGATION_ROWS: List[Tuple[int, str, str, int, int, str]] = [
    (1, "fildza@ur.unirazak.edu.my", None, 1, 45, "MEDIUM"),
    (2, "amin.demo@gmail.com", None, 3, 95, "HIGH"),
    (3, "nur.safe@example.com", None, 0, 10, "LOW"),
    (4, "amir.jobseek@gmail.com", None, 1, 55, "MEDIUM"),
    (5, "siti.telco@outlook.com", None, 1, 70, "MEDIUM"),
    (6, "farid.wallet@yahoo.com", None, 1, 90, "HIGH"),
    (7, "intan.professional@proton.me", None, 1, 83, "HIGH"),
    (8, "hafiz.lowrisk@example.com", None, 1, 20, "LOW"),
    (9, "mfildxza@gmail.com", "+601136005936", 2, 68, "MEDIUM"),
    (10, None, "+60135550011", 2, 82, "HIGH"),
]

BREACH_ROWS: List[Tuple[int, str, str, str]] = [
    (1, "EduForumDemo", "2024-02-11", "Email addresses, Passwords"),
    (2, "ShopLink", "2023-08-03", "Email addresses, Passwords, Full names"),
    (2, "PayTrack", "2022-11-19", "Financial Information, Phone numbers"),
    (2, "RewardsPortal", "2021-01-14", "Passwords, Date of birth"),
    (4, "MyJobPortal-MY", "2024-05-28", "Email addresses, Phone numbers, Address"),
    (5, "LocalTelco-Leaked", "2023-04-02", "Phone numbers, Address, Date of birth"),
    (
        6,
        "E-Wallet-Mega-Breach",
        "2025-01-07",
        "Financial Information, Passwords, Full names, Phone numbers",
    ),
    (7, "LinkedIn-RegionalDump", "2021-06-24", "Email addresses, Full names, Usernames"),
    (8, "NewsletterHub", "2021-11-07", "Email addresses, Usernames"),
    (9, "Shoppe-Marketplace", "2024-09-16", "Email addresses, Phone numbers"),
    (9, "MyJobPortal-MY", "2023-12-01", "Phone numbers, Address, Date of birth"),
    (10, "LocalTelco-Leaked", "2023-10-09", "Phone numbers, Address"),
    (10, "E-Wallet-Mega-Breach", "2025-01-07", "Phone numbers, Financial Information"),
]


def build_db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", MYSQL_DEFAULTS["host"]),
        "port": int(os.getenv("MYSQL_PORT", str(MYSQL_DEFAULTS["port"]))),
        "user": os.getenv("MYSQL_USER", MYSQL_DEFAULTS["user"]),
        "password": os.getenv("MYSQL_PASSWORD", MYSQL_DEFAULTS["password"]),
        "database": os.getenv("MYSQL_DATABASE", MYSQL_DEFAULTS["database"]),
        "use_pure": True,
    }


def seed_latest_data() -> None:
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

    insert_investigations = """
    INSERT INTO investigation_logs (id, email, phone_number, breach_count, risk_score, risk_level, checked_at)
    VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """

    insert_breaches = """
    INSERT INTO breach_results (investigation_id, breach_name, breach_date, data_exposed)
    VALUES (%s, %s, %s, %s)
    """

    with connect(**build_db_config()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_investigation_logs)
            cursor.execute(create_breach_results)
            cursor.execute("DELETE FROM breach_results")
            cursor.execute("DELETE FROM investigation_logs")

            cursor.executemany(insert_investigations, INVESTIGATION_ROWS)
            cursor.executemany(insert_breaches, BREACH_ROWS)
            cursor.execute("ALTER TABLE investigation_logs AUTO_INCREMENT = 11")

        conn.commit()


def verify_counts() -> Tuple[int, int]:
    with connect(**build_db_config()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM investigation_logs")
            investigation_count = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM breach_results")
            breach_count = int(cursor.fetchone()[0])

    return investigation_count, breach_count


if __name__ == "__main__":
    try:
        seed_latest_data()
        investigations, breaches = verify_counts()
        print("[OK] MySQL connected and latest mock data seeded.")
        print(f"[OK] investigation_logs rows: {investigations}")
        print(f"[OK] breach_results rows: {breaches}")
    except MySQLError as exc:
        print("[ERROR] Failed to connect/seed MySQL.")
        print(f"[ERROR] {exc}")
        raise SystemExit(1)
