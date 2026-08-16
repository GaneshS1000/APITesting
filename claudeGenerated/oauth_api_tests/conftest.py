"""
Pytest fixtures shared across all test modules.
"""
import pytest
from utils.api_client import OAuthAPIClient


@pytest.fixture(scope="session")
def api_client():
    """Single API client per test session (reuses TCP connection)."""
    client = OAuthAPIClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def access_token(api_client):
    """
    Fetches a valid access token once per session and shares it
    with any test that needs an authenticated resource call.
    """
    response = api_client.get_access_token()
    assert response.status_code == 200, (
        f"Failed to obtain access token. "
        f"Status: {response.status_code}, Body: {response.text}"
    )
    token = response.json().get("access_token")
    assert token, "access_token not present in token response"
    return token


def pytest_html_report_title(report):
    report.title = "OAuth API Test Report"
