#!/usr/bin/env python
"""
Create PostgreSQL databases for EST services
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
import sys
from pathlib import Path

# Database configuration
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432

DATABASES = ["est_auth", "est_catalog"]

project_root = Path(__file__).parent


def create_databases():
    """Create the databases if they don't exist"""
    print("Connecting to PostgreSQL server...")
    try:
        # Connect to PostgreSQL server (not a specific database)
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        for db_name in DATABASES:
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,)
            )
            exists = cursor.fetchone()

            if exists:
                print(f"✓ Database '{db_name}' already exists")
            else:
                print(f"Creating database '{db_name}'...")
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"✓ Database '{db_name}' created")

        cursor.close()
        conn.close()
        print("\n✓ All databases ready\n")
        return True

    except psycopg2.OperationalError as e:
        print(f"\n❌ Error: Could not connect to PostgreSQL server")
        print(f"   {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Connection details are correct:")
        print(f"     - Host: {POSTGRES_HOST}")
        print(f"     - Port: {POSTGRES_PORT}")
        print(f"     - User: {POSTGRES_USER}")
        print(f"     - Password: {POSTGRES_PASSWORD}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def run_migrations():
    """Run Alembic migrations for each service"""
    print("Running database migrations...\n")

    migrations = [
        ("Auth Service", "alembic_auth.ini"),
        ("Catalog Service", "alembic_catalog.ini"),
    ]

    for service_name, config_file in migrations:
        print(f"Migrating {service_name}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "-c", config_file, "upgrade", "head"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✓ {service_name} migrations complete")
            else:
                print(f"❌ {service_name} migration failed:")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Error running {service_name} migrations: {e}")
            return False

    print("\n✓ All migrations complete\n")
    return True


def main():
    print("\n" + "="*60)
    print("EST Backend - Database Setup")
    print("="*60 + "\n")

    # Step 1: Create databases
    if not create_databases():
        sys.exit(1)

    # Step 2: Run migrations
    if not run_migrations():
        sys.exit(1)

    print("="*60)
    print("✓ Database setup complete!")
    print("="*60)
    print("\nYou can now start the services with:")
    print("  python run_services.py")
    print()


if __name__ == "__main__":
    main()
