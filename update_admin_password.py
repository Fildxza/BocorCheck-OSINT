"""
Update Admin Password
Change the admin user's password safely
"""

import os
import sys
import getpass
from mysql.connector import connect, Error as MySQLError
from auth import verify_password, hash_password


def get_db_config() -> dict:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }


def update_admin_password():
    """Update admin user's password"""
    
    print("=" * 70)
    print("Update Admin Password - BocorCheck")
    print("=" * 70)
    
    cfg = get_db_config()
    
    try:
        with connect(**cfg) as conn:
            with conn.cursor(dictionary=True) as cursor:
                # Get current admin user
                cursor.execute("""
                    SELECT id, username, email, password_hash
                    FROM users
                    WHERE username = 'admin'
                """)
                
                admin = cursor.fetchone()
                if not admin:
                    print("\n✗ Admin user not found!")
                    print("Run: python setup_admin.py")
                    return False
                
                print(f"\nAdmin User Found:")
                print(f"  Username: {admin['username']}")
                print(f"  Email: {admin['email']}")
                
                # Verify current password
                print(f"\n1️⃣  Verify Current Password:")
                current_password = getpass.getpass("  Enter current admin password: ")
                
                if not verify_password(current_password, admin['password_hash']):
                    print("  ✗ Password incorrect!")
                    return False
                print("  ✓ Password verified")
                
                # Get new password
                print(f"\n2️⃣  Enter New Password:")
                new_password = getpass.getpass("  New password (16+ chars recommended): ")
                confirm_password = getpass.getpass("  Confirm new password: ")
                
                if new_password != confirm_password:
                    print("  ✗ Passwords don't match!")
                    return False
                
                if len(new_password) < 8:
                    print("  ✗ Password must be at least 8 characters!")
                    return False
                
                # Hash new password
                new_hash = hash_password(new_password)
                
                # Update database
                cursor.execute("""
                    UPDATE users
                    SET password_hash = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_hash, admin['id']))
                
                conn.commit()
                
                print(f"\n✓ Admin password updated successfully!")
                print(f"\nYou can now login with:")
                print(f"  Username: {admin['username']}")
                print(f"  Password: [your new password]")
                
                return True
                
    except MySQLError as e:
        print(f"\n✗ Database error: {e}")
        return False


if __name__ == "__main__":
    success = update_admin_password()
    sys.exit(0 if success else 1)
