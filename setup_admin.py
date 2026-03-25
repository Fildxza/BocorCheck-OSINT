"""
Setup Admin User for BocorCheck
Creates admin user in the users table with bcrypt-hashed password
Run this once to create admin account
"""

import os
from auth import create_user, check_user_exists


def setup_admin_user():
    """Create default admin user"""
    
    # Admin credentials
    admin_username = "admin"
    admin_email = "admin@bocorcheck.local"
    admin_password = "Admin123!"  # Default password - CHANGE THIS!
    
    print("=" * 70)
    print("BocorCheck Admin User Setup")
    print("=" * 70)
    
    # Check if admin already exists
    exists = check_user_exists(username=admin_username, email=admin_email)
    if exists:
        print("\n✗ Admin user already exists!")
        print(f"  Username: {admin_username}")
        print(f"  Email: {admin_email}")
        print("\nTo change admin password, use:")
        print("  python update_admin_password.py")
        return False
    
    # Create admin user
    print(f"\nCreating admin user...")
    print(f"  Username: {admin_username}")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print(f"  Role: admin")
    
    try:
        result = create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role='admin'  # Set role to admin
        )
        
        if result:
            print("\n✓ Admin user created successfully!")
            print("\nDEFAULT LOGIN CREDENTIALS:")
            print("=" * 70)
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
            print(f"Email: {admin_email}")
            print("=" * 70)
            print("\n⚠️  IMPORTANT SECURITY NOTES:")
            print("  1. Change the default password immediately after first login")
            print("  2. Use strong password (16+ chars, mix of upper/lower/numbers/special)")
            print("  3. Do NOT share admin credentials")
            print("  4. Admin account has access to all user data")
            print("=" * 70)
            return True
        else:
            print("\n✗ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"\n✗ Error creating admin user: {e}")
        return False


if __name__ == "__main__":
    success = setup_admin_user()
    exit(0 if success else 1)
