"""
Reusable API client wrapping requests.
Centralises HTTP calls so tests stay declarative.
"""
import requests
from typing import Optional, Dict, Any
from config.config import Config


class OAuthAPIClient:
    """Thin wrapper around the OAuth + Course Details endpoints."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    # ---------- Token endpoint ----------
    def get_access_token(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        grant_type: Optional[str] = None,
        scope: Optional[str] = None,
        omit: Optional[list] = None,
    ) -> requests.Response:
        """
        POST to the token endpoint. Any field can be overridden or omitted
        (pass field name in `omit` list) to support negative tests.
        """
        payload = {
            "client_id": client_id if client_id is not None else Config.CLIENT_ID,
            "client_secret": client_secret if client_secret is not None else Config.CLIENT_SECRET,
            "grant_type": grant_type if grant_type is not None else Config.GRANT_TYPE,
            "scope": scope if scope is not None else Config.SCOPE,
        }
        if omit:
            for field in omit:
                payload.pop(field, None)

        return self.session.post(
            Config.token_url(),
            data=payload,  # form-encoded (matches the Postman formdata)
            timeout=self.timeout,
        )

    # ---------- Resource endpoint ----------
    def get_course_details(
        self,
        access_token: Optional[str] = None,
        include_token: bool = True,
    ) -> requests.Response:
        """GET course details, optionally without a token for negative tests."""
        params: Dict[str, Any] = {}
        if include_token and access_token is not None:
            params["access_token"] = access_token

        return self.session.get(
            Config.course_url(),
            params=params,
            timeout=self.timeout,
        )

    def close(self):
        self.session.close()
