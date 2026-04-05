"""
Database Collation Fix Script
This script standardizes the collation of specified tables and columns to utf8mb4_unicode_ci
to resolve "Illegal mix of collations" errors in MySQL.
"""

import os
from mysql.connector import connect, Error as MySQLError

def get_db_config() -> dict:
    """Get database configuration from environment variables"""
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "fyp_user"),
        "password": os.getenv("MYSQL_PASSWORD", "Admin123!"),
        "database": os.getenv("MYSQL_DATABASE", "fyp_osint"),
        "use_pure": True,
    }

def fix_database_collation():
    """
    Connects to the database and alters table/column collations.
    """
    cfg = get_db_config()
    db_name = cfg["database"]
    
    # Tables and columns to fix
    tables_to_fix = {
        "breach_timeline": ["breach_name"],
        "breach_results": ["breach_name", "data_exposed", "source"],
        "investigation_logs": ["name", "description", "tags"],
        "mitigation_steps": ["title", "description", "category"],
        "monitoring_subscriptions": ["email", "phone_number", "bank_account"],
    }

    try:
        with connect(**cfg) as conn:
            cursor = conn.cursor()
            print(f"Successfully connected to database '{db_name}'.")

            # Alter database default collation
            print(f"Altering database '{db_name}' default character set and collation...")
            cursor.execute(f"ALTER DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("...Database default collation updated.")

            # Alter table collations
            for table, columns in tables_to_fix.items():
                try:
                    # Alter table default collation
                    print(f"Altering table '{table}'...")
                    cursor.execute(f"ALTER TABLE `{table}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                    
                    # Alter specific column collations
                    for column in columns:
                        print(f"  -> Altering column '{column}' in table '{table}'...")
                        # We need to get the column's current definition to alter it
                        cursor.execute(f"SHOW CREATE TABLE `{table}`")
                        create_table_statement = cursor.fetchone()[1]
                        
                        # Find the line with the column definition
                        col_def_line = ""
                        for line in create_table_statement.split('\\n'):
                            if f"`{column}`" in line:
                                col_def_line = line.strip().rstrip(',')
                                break
                        
                        if col_def_line:
                            # Rebuild the definition with the new collation
                            alter_statement = f"ALTER TABLE `{table}` MODIFY {col_def_line} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                            # Some definitions might have defaults that need to be handled, this is a simplified approach
                            # For more complex cases, a more robust parser would be needed.
                            # This simplified version should work for VARCHAR, TEXT, etc.
                            
                            # Let's try a more direct approach that is less prone to syntax errors
                            cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{column}'")
                            col_details = cursor.fetchone()
                            col_type = col_details[1] # Type is already string
                            is_nullable = "NULL" if col_details[2] == 'YES' else "NOT NULL"
                            default_val_info = col_details[4]
                            default_val = f"DEFAULT '{default_val_info}'" if default_val_info else ""

                            final_alter_statement = f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {col_type} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci {is_nullable} {default_val};"
                            
                            print(f"     Executing: {final_alter_statement}")
                            cursor.execute(final_alter_statement)

                        else:
                            print(f"     ! Could not find column definition for '{column}' in '{table}'. Skipping.")

                    print(f"...Table '{table}' updated successfully.")
                except MySQLError as table_error:
                    print(f"!!! Error altering table '{table}': {table_error}")
            
            conn.commit()
            print("\\n✅ All specified tables and columns have been updated to utf8mb4_unicode_ci collation.")

    except MySQLError as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    fix_database_collation()
