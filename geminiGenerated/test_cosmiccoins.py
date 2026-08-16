import pytest
import requests

BASE_URL = "https://template.postman-echo.com/api/v1"


@pytest.fixture(scope="module")
def api_context():
    """
    A fixture to share data (like account IDs) between test steps.
    """
    return {
        "auth_token": None,
        "account_id": None
    }


def test_01_authentication(api_context):
    """Test the GET /auth endpoint."""
    url = f"{BASE_URL}/auth"
    response = requests.get(url)

    assert response.status_code == 200
    # Assuming the API returns a token or success message
    print("\nAuthentication Successful")


def test_02_create_account(api_context):
    """Test the POST /accounts endpoint."""
    url = f"{BASE_URL}/accounts"
    payload = {
        "owner": "Cosmo Wanderer",
        "balance": 0,
        "currency": "COSMIC_COINS"
    }

    response = requests.post(url, json=payload)

    assert response.status_code in [200, 201]
    data = response.json()

    # Capture the ID for the next integration step
    assert "id" in data or "data" in data
    api_context["account_id"] = data.get("id") or data.get("data", {}).get("id")
    print(f"\nAccount Created with ID: {api_context['account_id']}")


def test_03_get_account_by_id(api_context):
    """Test the GET /accounts/:id endpoint using the ID from step 2."""
    if not api_context["account_id"]:
        pytest.skip("Account ID not found from previous step.")

    url = f"{BASE_URL}/accounts/{api_context['account_id']}"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.json()["currency"] == "COSMIC_COINS"


def test_04_get_locations(api_context):
    """Test the GET /locations endpoint."""
    url = f"{BASE_URL}/locations"
    response = requests.get(url)

    assert response.status_code == 200
    assert isinstance(response.json(), (list, dict))
    print(f"\nLocations retrieved: {len(response.json())} items found.")