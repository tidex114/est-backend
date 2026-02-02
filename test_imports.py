"""
Quick test to verify the API is working correctly.
"""
import sys
sys.path.insert(0, r"C:\Users\skyde\PycharmProjects\est-backend")

print("Testing imports...")

try:
    from services.catalog.src.main import app
    print("✓ Main app imported successfully")

    from services.catalog.src.api.offers import router
    print("✓ API router imported successfully")

    from services.catalog.src.services.offers import OfferService
    print("✓ Service layer imported successfully")

    from services.catalog.src.repo.offers_repo import OffersRepo
    print("✓ Repository imported successfully")

    from services.catalog.src.domain.offer import Offer, Money
    print("✓ Domain models imported successfully")

    from services.catalog.src.schemas.offer import OfferCreate, OfferOut
    print("✓ Schemas imported successfully")

    from services.catalog.src.core.dependencies import get_db, require_partner, require_user
    print("✓ Dependencies imported successfully")

    print("\n✅ All imports successful! The API is ready to run.")
    print("\nTo start the server, run:")
    print("  uvicorn services.catalog.src.main:app --reload")

    # Print available routes
    print("\n📋 Available API Routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"  {methods:12} {route.path}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
