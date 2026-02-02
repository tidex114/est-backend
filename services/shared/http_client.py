"""
HTTP Client for Inter-Service Communication
Used for service-to-service calls (e.g., catalog calling auth to validate token)
"""
import httpx
from typing import Optional, Dict, Any
from services.shared.exceptions import ExternalServiceError


class ServiceHTTPClient:
    """HTTP client for inter-service communication"""

    def __init__(self, service_url: str, timeout: float = 5.0):
        self.service_url = service_url
        self.timeout = timeout

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make GET request to service"""
        try:
            url = f"{self.service_url}{endpoint}"
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Failed to call {self.service_url}: {str(e)}")

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request to service"""
        try:
            url = f"{self.service_url}{endpoint}"
            with httpx.Client() as client:
                response = client.post(url, json=data, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Failed to call {self.service_url}: {str(e)}")

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Call auth service to validate JWT token

        Returns token claims if valid, raises exception if invalid
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.get("/auth/validate", headers=headers)
