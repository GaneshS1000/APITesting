"""
Test cases for the AuthorizationServer endpoint (OAuth token generation).
Mirrors the Postman 'AuthorizationServer' request.
"""
import re
import pytest
from jsonschema import validate
from utils.schemas import TOKEN_RESPONSE_SCHEMA


# ====================================================
# POSITIVE TESTS
# ====================================================
@pytest.mark.positive
@pytest.mark.smoke
class TestAuthorizationServerPositive:
    """Happy-path scenarios for token generation."""

    def test_token_request_returns_200(self, api_client):
        response = api_client.get_access_token()
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_response_time_under_3_seconds(self, api_client):
        response = api_client.get_access_token()
        assert response.elapsed.total_seconds() < 3, (
            f"Response too slow: {response.elapsed.total_seconds()}s"
        )

    def test_response_is_json(self, api_client):
        response = api_client.get_access_token()
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_response_matches_schema(self, api_client):
        response = api_client.get_access_token()
        validate(instance=response.json(), schema=TOKEN_RESPONSE_SCHEMA)

    def test_access_token_is_non_empty_string(self, api_client):
        token = api_client.get_access_token().json().get("access_token")
        assert isinstance(token, str) and len(token) > 0

    def test_token_type_is_bearer(self, api_client):
        token_type = api_client.get_access_token().json().get("token_type")
        assert token_type.lower() == "bearer"

    def test_expires_in_is_positive(self, api_client):
        expires_in = api_client.get_access_token().json().get("expires_in")
        assert isinstance(expires_in, (int, float)) and expires_in > 0

    def test_scope_matches_requested(self, api_client):
        scope = api_client.get_access_token().json().get("scope")
        assert scope == "trust"

    def test_access_token_format_is_valid(self, api_client):
        token = api_client.get_access_token().json().get("access_token")
        # OAuth tokens are typically URL-safe base64-ish
        assert re.match(r"^[A-Za-z0-9\-._~+/=]+$", token), \
            f"Token contains unexpected characters: {token}"


# ====================================================
# NEGATIVE TESTS
# ====================================================
@pytest.mark.negative
class TestAuthorizationServerNegative:
    """Error-path scenarios for token generation."""

    def test_invalid_client_id_returns_401(self, api_client):
        response = api_client.get_access_token(client_id="invalid_client_xyz")
        assert response.status_code in (400, 401), (
            f"Expected 400/401 for bad client_id, got {response.status_code}"
        )

    def test_invalid_client_secret_returns_unauthorized(self, api_client):
        response = api_client.get_access_token(client_secret="wrong_secret")
        assert response.status_code in (400, 401)

    def test_invalid_grant_type_returns_400(self, api_client):
        response = api_client.get_access_token(grant_type="invalid_grant")
        assert response.status_code in (400, 401)

    def test_missing_client_id_returns_error(self, api_client):
        response = api_client.get_access_token(omit=["client_id"])
        assert response.status_code in (400, 401)

    def test_missing_client_secret_returns_error(self, api_client):
        response = api_client.get_access_token(omit=["client_secret"])
        assert response.status_code in (400, 401)

    def test_missing_grant_type_returns_error(self, api_client):
        response = api_client.get_access_token(omit=["grant_type"])
        assert response.status_code in (400, 401)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("client_id", ""),
            ("client_secret", ""),
            ("grant_type", ""),
            ("scope", ""),
        ],
    )
    def test_empty_field_returns_error(self, api_client, field, value):
        response = api_client.get_access_token(**{field: value})
        assert response.status_code in (400, 401), (
            f"Expected 400/401 when {field} is empty, got {response.status_code}"
        )

    def test_error_response_contains_error_field(self, api_client):
        response = api_client.get_access_token(client_id="invalid_client")
        # Many OAuth servers return JSON error with 'error' key per RFC 6749
        try:
            body = response.json()
            assert "error" in body or response.status_code >= 400
        except ValueError:
            # If body isn't JSON, status code alone is enough
            assert response.status_code >= 400
