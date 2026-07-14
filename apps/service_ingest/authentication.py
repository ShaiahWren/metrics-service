"""Service-to-service token authentication for the ingest endpoint."""

import logging
import secrets

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class ServiceUser:
    """Minimal user-like object satisfying DRF's IsAuthenticated check."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self.is_authenticated = True

    def __bool__(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"service:{self.service_name}"


class ServiceTokenAuthentication(BaseAuthentication):
    """
    Validates X-ANSIBLE-SERVICE-AUTH header against SERVICE_INGEST_TOKENS setting.

    SERVICE_INGEST_TOKENS is a dict mapping service_name → token string.
    On success sets request.user to a ServiceUser and request.auth to service_name.

    POC: tokens are static env-var-configured values.
    Full implementation: validate against gateway-issued per-service tokens.
    """

    HEADER = "HTTP_X_ANSIBLE_SERVICE_AUTH"

    def authenticate(self, request):
        token = request.META.get(self.HEADER, "").strip()
        if not token:
            return None  # no credentials presented; let other authenticators try

        tokens: dict = getattr(settings, "SERVICE_INGEST_TOKENS", {})
        if not tokens:
            logger.warning("SERVICE_INGEST_TOKENS is not configured; rejecting service auth")
            raise AuthenticationFailed("Service authentication is not configured")

        for service_name, service_token in tokens.items():
            if secrets.compare_digest(token, service_token):
                logger.debug("Authenticated service: %s", service_name)
                return (ServiceUser(service_name), service_name)

        raise AuthenticationFailed("Invalid service token")

    def authenticate_header(self, request) -> str:
        return "X-ANSIBLE-SERVICE-AUTH"
