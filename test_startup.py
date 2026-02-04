#!/usr/bin/env python
"""Test script to verify services can start up"""
import sys

try:
    print("Loading auth settings...")
    from services.auth.src.core.settings import settings as auth_settings
    print(f"  ✓ Auth settings loaded. Database: {auth_settings.database_url}")

    print("\nLoading auth main app...")
    from services.auth.src.main import app as auth_app
    print(f"  ✓ Auth app loaded: {auth_app.title}")

    print("\nLoading catalog settings...")
    from services.catalog.src.core.settings import settings as catalog_settings
    print(f"  ✓ Catalog settings loaded. Database: {catalog_settings.database_url}")

    print("\nLoading catalog main app...")
    from services.catalog.src.main import app as catalog_app
    print(f"  ✓ Catalog app loaded: {catalog_app.title}")

    print("\n" + "="*50)
    print("SUCCESS: Both services loaded successfully!")
    print("="*50)
    sys.exit(0)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
