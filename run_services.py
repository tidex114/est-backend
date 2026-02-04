#!/usr/bin/env python
"""Simple script to test starting services"""
import subprocess
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent
auth_service = None
catalog_service = None


def start_service(name: str, app_path: str, host: str, port: int) -> subprocess.Popen:
    print(f"Starting {name} Service on port {port}...")
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            app_path,
            "--host", host,
            "--port", str(port),
            "--reload",
        ],
        cwd=str(project_root),
        stdout=None,
        stderr=None,
    )
    time.sleep(2)
    if proc.poll() is not None:
        raise RuntimeError(f"{name} service failed to start. See logs above.")
    print(f"✓ {name} service started (PID: {proc.pid})")
    return proc


try:
    print("\n" + "="*60)
    print("EST Backend - Service Startup Test")
    print("="*60)
    print()

    # Start auth service
    auth_service = start_service("Auth", "services.auth.src.main:app", "127.0.0.1", 8001)

    time.sleep(1)

    # Start catalog service
    catalog_service = start_service("Catalog", "services.catalog.src.main:app", "127.0.0.1", 8000)

    print()
    print("="*60)
    print("Services Running!")
    print("="*60)
    print()
    print("Auth Service:     http://localhost:8001/docs")
    print("Catalog Service:  http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop services...")
    print()

    # Wait for keyboard interrupt
    auth_service.wait()

except KeyboardInterrupt:
    print("\n\nShutting down services...")
    if auth_service:
        auth_service.terminate()
        auth_service.wait(timeout=5)
        print("✓ Auth service stopped")

    if catalog_service:
        catalog_service.terminate()
        catalog_service.wait(timeout=5)
        print("✓ Catalog service stopped")

    print("\nServices stopped.")
    sys.exit(0)

except Exception as e:
    print(f"\nERROR: {e}")
    if auth_service:
        auth_service.terminate()
    if catalog_service:
        catalog_service.terminate()
    sys.exit(1)
