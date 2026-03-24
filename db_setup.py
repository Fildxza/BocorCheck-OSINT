import os
import sys
from typing import List

from mysql.connector import Error as MySQLError
from mysql.connector import connect


def get_db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }


def ddl_statements() -> List[str]:
    return [
        """
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
        """,
        """
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
        """,
        """
        CREATE TABLE IF NOT EXISTS breach_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            investigation_id INT NOT NULL,
            breach_name VARCHAR(255) NOT NULL,
            breach_date DATE NULL,
            data_exposed TEXT,
            CONSTRAINT fk_breach_investigation
                FOREIGN KEY (investigation_id)
                REFERENCES investigation_logs(id)
                ON DELETE CASCADE,
            INDEX idx_breach_investigation_id (investigation_id),
            INDEX idx_breach_date (breach_date)
        ) ENGINE=InnoDB
        """,
        """
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
        """,
        """
        CREATE TABLE IF NOT EXISTS risk_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            investigation_id INT NOT NULL,
            breach_count INT,
            sensitive_data BOOLEAN,
            risk_score INT,
            risk_level VARCHAR(10),
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_risk_scores_investigation
                FOREIGN KEY (investigation_id)
                REFERENCES investigation_logs(id)
                ON DELETE CASCADE,
            INDEX idx_risk_scores_investigation_id (investigation_id),
            INDEX idx_risk_scores_level (risk_level),
            INDEX idx_risk_scores_created_at (created_at)
        ) ENGINE=InnoDB
        """,
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            investigation_id INT NOT NULL,
            alert_type VARCHAR(50),
            message TEXT,
            status VARCHAR(20),
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_alerts_investigation
                FOREIGN KEY (investigation_id)
                REFERENCES investigation_logs(id)
                ON DELETE CASCADE,
            INDEX idx_alerts_investigation_id (investigation_id),
            INDEX idx_alerts_status (status),
            INDEX idx_alerts_sent_at (sent_at),
            UNIQUE KEY uq_alert_per_investigation_type (investigation_id, alert_type)
        ) ENGINE=InnoDB
        """,
    ]


def migration_statements() -> List[str]:
    """
    Migration SQL statements for backward compatibility.
    These are safe to run multiple times (IF NOT EXISTS, IF EXISTS checks).
    """
    return [
        """
        ALTER TABLE investigation_logs 
        ADD COLUMN user_id INT NULL 
        CONSTRAINT fk_investigation_user 
            FOREIGN KEY (user_id) 
            REFERENCES users(id) 
            ON DELETE SET NULL,
        ADD INDEX idx_investigation_user_id (user_id)
        """,
    ]


def apply_migrations(conn) -> None:
    """
    Safely apply migration statements. Silently skip if columns already exist.
    """
    try:
        with conn.cursor() as cursor:
            for stmt in migration_statements():
                try:
                    cursor.execute(stmt)
                except MySQLError as e:
                    # Skip errors about duplicate columns (error 1060)
                    if e.errno != 1060:
                        raise
            conn.commit()
    except MySQLError as e:
        # Log but don't fail during migrations
        print(f"Migration note: {e}")


def main() -> int:
    cfg = get_db_config()

    try:
        with connect(**cfg) as conn:
            # Create tables
            with conn.cursor() as cursor:
                for stmt in ddl_statements():
                    cursor.execute(stmt)
            conn.commit()

            # Apply migrations for backward compatibility
            apply_migrations(conn)

            # Display schema status
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = sorted(row[0] for row in cursor.fetchall())

        print("✓ MySQL schema is ready.")
        print(f"✓ Tables: {', '.join(tables)}")
        return 0

    except MySQLError as exc:
        print(f"✗ Could not prepare MySQL schema: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
