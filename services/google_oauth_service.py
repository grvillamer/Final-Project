"""
Google OAuth 2.0 sign-in (desktop / local Flet host).

Uses the Google OAuth Desktop / installed-client flow via a localhost redirect listener.
Ensure your Google Cloud OAuth client allows redirect URIs for the configured port.

See .env.local (and env.example.txt) for required variables.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from google_auth_oauthlib.flow import InstalledAppFlow

from config import config

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"


@dataclass
class GoogleProfile:
    sub: str
    email: str
    verified_email: bool
    given_name: str
    family_name: str
    picture: Optional[str]


class GoogleOAuthConfigurationError(RuntimeError):
    """Raised when Google OAuth credentials are missing or placeholders."""


class GoogleOAuthFlowError(RuntimeError):
    """Raised when OAuth exchange or profile fetch fails."""


def google_oauth_configured() -> bool:
    cid = (config.GOOGLE_CLIENT_ID or "").strip()
    cs = (config.GOOGLE_CLIENT_SECRET or "").strip()
    if not cid or not cs:
        return False
    cid_u, cs_u = cid.upper(), cs.upper()
    placeholders = ("YOUR_GOOGLE_OAUTH", "YOUR-GOOGLE-CLIENT", "CHANGEME", "REPLACE_ME")
    if any(tok in cid_u or tok in cs_u for tok in placeholders):
        return False
    bad = ("your-google-client-id", "your-google-client-secret")
    lc = cid.lower()
    lb = cs.lower()
    return not any(tok in lc or tok in lb for tok in bad)


def _installed_client_json() -> Dict[str, Any]:
    """Build an 'installed' OAuth client descriptor from environment variables."""
    port = config.GOOGLE_OAUTH_REDIRECT_PORT
    return {
        "installed": {
            "client_id": config.GOOGLE_CLIENT_ID.strip(),
            "client_secret": config.GOOGLE_CLIENT_SECRET.strip(),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [f"http://localhost:{port}/", f"http://127.0.0.1:{port}/"],
        }
    }


def fetch_google_profile() -> GoogleProfile:
    """
    Start Google OAuth in the user's browser and complete authentication on localhost.
    """
    if not google_oauth_configured():
        raise GoogleOAuthConfigurationError(
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.local with real credentials "
            "from Google Cloud Console (see comments in .env.local). Placeholder values cannot sign in."
        )

    flow = InstalledAppFlow.from_client_config(
        _installed_client_json(),
        scopes=SCOPES,
    )

    credentials = flow.run_local_server(
        port=config.GOOGLE_OAUTH_REDIRECT_PORT,
        prompt="consent",
        access_type="offline",
        open_browser=True,
        authorization_prompt_message=(
            "[Google Sign-In] A browser window should open shortly. Complete sign-in "
            "and return to SpottEd when finished."
        ),
        success_message="Sign-in finished. You can close this browser tab.",
    )

    if not credentials.token:
        raise GoogleOAuthFlowError("Google OAuth did not return an access token.")

    resp = requests.get(
        USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=30,
    )

    if not resp.ok:
        raise GoogleOAuthFlowError(f"Google userinfo error: HTTP {resp.status_code}")

    data = resp.json()
    sub = data.get("sub")
    email = data.get("email")
    verified = bool(data.get("verified_email"))
    if not sub or not email:
        raise GoogleOAuthFlowError("Google account did not return a valid profile (missing sub/email).")

    return GoogleProfile(
        sub=sub,
        email=str(email),
        verified_email=verified,
        given_name=str(data.get("given_name") or ""),
        family_name=str(data.get("family_name") or ""),
        picture=data.get("picture"),
    )
