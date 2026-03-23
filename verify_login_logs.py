import requests
from mysql.connector import connect

BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"User-Agent": "Copilot-Login-Test/1.0"}


def main() -> None:
    session = requests.Session()

    # Failed login
    session.post(
        f"{BASE_URL}/admin/login",
        data={"username": "admin", "password": "wrongpass"},
        headers=HEADERS,
        timeout=10,
    )

    # Successful login
    session.post(
        f"{BASE_URL}/admin/login",
        data={"username": "admin", "password": "admin123"},
        headers=HEADERS,
        timeout=10,
    )

    # Logout
    session.get(f"{BASE_URL}/admin/logout", headers=HEADERS, timeout=10)

    conn = connect(
        host="127.0.0.1",
        port=3306,
        user="fyp_user",
        password="Admin123!",
        database="fyp_osint",
        use_pure=True,
    )

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT username, role, action, ip_address, LEFT(user_agent, 60), created_at
            FROM login_logs
            ORDER BY id DESC
            LIMIT 6
            """
        )
        rows = cursor.fetchall()

    conn.close()

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
