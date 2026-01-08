import os

# Taiga official docker image uses DJANGO_SETTINGS_MODULE=settings.config.
# We extend that config here so DB/events/etc continue to work.
from .config import *  # noqa

INSTALLED_APPS += [
    "mozilla_django_oidc",
    "taiga_contrib_oidc_auth",
]

AUTHENTICATION_BACKENDS = list(AUTHENTICATION_BACKENDS) + [
    "taiga_contrib_oidc_auth.oidc.TaigaOIDCAuthenticationBackend",
]

# Mount OIDC urls under /api/oidc/ (see settings/urls.py)
ROOT_URLCONF = "settings.urls"

OIDC_CALLBACK_CLASS = "taiga_contrib_oidc_auth.views.TaigaOIDCAuthenticationCallbackView"
OIDC_RP_SCOPES = os.getenv("OIDC_RP_SCOPES", "openid profile email")
OIDC_RP_SIGN_ALGO = os.getenv("OIDC_RP_SIGN_ALGO", "RS256")

OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID", "taiga")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET", "change_me_taiga_oidc_client_secret")

# Keycloak endpoints
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv(
    "OIDC_OP_AUTHORIZATION_ENDPOINT",
    "http://keycloak:8080/id/realms/opshub/protocol/openid-connect/auth",
)
OIDC_OP_TOKEN_ENDPOINT = os.getenv(
    "OIDC_OP_TOKEN_ENDPOINT",
    "http://keycloak:8080/id/realms/opshub/protocol/openid-connect/token",
)
OIDC_OP_USER_ENDPOINT = os.getenv(
    "OIDC_OP_USER_ENDPOINT",
    "http://keycloak:8080/id/realms/opshub/protocol/openid-connect/userinfo",
)
OIDC_OP_JWKS_ENDPOINT = os.getenv(
    "OIDC_OP_JWKS_ENDPOINT",
    "http://keycloak:8080/id/realms/opshub/protocol/openid-connect/certs",
)
