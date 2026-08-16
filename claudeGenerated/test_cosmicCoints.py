"""
=============================================================================
Integration Test Suite
APIs Under Test:
  GET  /api/v1/auth
  POST /api/v1/accounts
  GET  /api/v1/accounts/:id
  GET  /api/v1/locations
=============================================================================
Run:
    pip install pytest requests
    pytest test_api_integration.py -v
    pytest test_api_integration.py -v --html=report.html   # with pytest-html
=============================================================================
"""

import pytest
import requests
import random
import string

# ─────────────────────────────────────────────
# Base Configuration
# ─────────────────────────────────────────────

BASE_URL      = "https://template.postman-echo.com/api/v1"
AUTH_URL      = f"{BASE_URL}/auth"
ACCOUNTS_URL  = f"{BASE_URL}/accounts"
LOCATIONS_URL = f"{BASE_URL}/locations"

VALID_CURRENCY       = "COSMIC_COINS"
VALID_CURRENCIES     = ["COSMIC_COINS", "MOON_BUCKS", "GALAXY_GOLD"]
VALID_CURRENCY_CODES = ["CC", "MB", "GG"]
KNOWN_PLANETS        = [
    "Mercury", "Mars",    "Jupiter",   # COSMIC_COINS ATMs
    "Titan",   "Europa",  "Enceladus", # MOON_BUCKS ATMs
    "Venus",   "Saturn",  "Uranus",    # GALAXY_GOLD ATMs
]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def random_name() -> str:
    """Generate a random full name mimicking Postman's $randomFirstName $randomLastName."""
    first = random.choice(string.ascii_uppercase) + \
            "".join(random.choices(string.ascii_lowercase, k=6))
    last  = random.choice(string.ascii_uppercase) + \
            "".join(random.choices(string.ascii_lowercase, k=7))
    return f"{first} {last}"


def auth_headers(api_key: str) -> dict:
    return {
        "x-api-key":    api_key,
        "Content-Type": "application/json",
    }


# ─────────────────────────────────────────────
# Session-scoped Fixtures
# ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_key():
    """
    Fetch the API key ONCE per test session from GET /auth.
    Real response: {"apiKey": "s0oCX9Q2.1KnGanOwFrLt5ZnDMqGEm"}
    """
    resp = requests.get(AUTH_URL)
    assert resp.status_code == 200, f"Auth failed: {resp.status_code}"
    data = resp.json()
    key  = data.get("apiKey") or data.get("token") or data.get("access_token")
    assert key, f"No API key found in auth response: {data}"
    return key


@pytest.fixture(scope="session")
def created_account(api_key):
    """
    Create one account at session start; reused by all GET /accounts/:id tests.
    Returns the full account response dict.
    """
    payload = {
        "owner":    random_name(),
        "balance":  0,
        "currency": VALID_CURRENCY,
    }
    resp = requests.post(
        ACCOUNTS_URL,
        json=payload,
        headers=auth_headers(api_key),
    )
    assert resp.status_code == 201, (
        f"Session fixture: account creation failed: {resp.status_code} | {resp.text}"
    )
    return resp.json()


@pytest.fixture
def account_payload():
    """Fresh random payload for each individual test."""
    return {
        "owner":    random_name(),
        "balance":  0,
        "currency": VALID_CURRENCY,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 1 — GET /auth
# ══════════════════════════════════════════════════════════════════════════════

class TestGetAuth:
    """Validates the authentication endpoint  GET /api/v1/auth"""

    def test_status_code_200(self):
        """Auth endpoint must return HTTP 200 OK."""
        resp = requests.get(AUTH_URL)
        assert resp.status_code == 200, \
            f"Expected 200, got {resp.status_code}"

    def test_response_is_valid_json(self):
        """Response body must be parseable JSON."""
        resp = requests.get(AUTH_URL)
        try:
            resp.json()
        except ValueError:
            pytest.fail("Auth response is not valid JSON")

    def test_response_contains_api_key_field(self):
        """Response JSON must contain the 'apiKey' field."""
        resp = requests.get(AUTH_URL)
        data = resp.json()
        assert "apiKey" in data, \
            f"'apiKey' not found in response: {data}"

    def test_api_key_is_non_empty_string(self):
        """apiKey value must be a non-empty string."""
        resp = requests.get(AUTH_URL)
        key  = resp.json().get("apiKey")
        assert isinstance(key, str) and len(key) > 0, \
            f"apiKey is empty or not a string: {key}"

    def test_api_key_contains_dot_separator(self):
        """apiKey must follow 'prefix.secret' format."""
        resp = requests.get(AUTH_URL)
        key  = resp.json().get("apiKey", "")
        assert "." in key, \
            f"apiKey does not contain a '.' separator: {key}"

    def test_content_type_is_json(self):
        """Content-Type header must be application/json."""
        resp = requests.get(AUTH_URL)
        ct   = resp.headers.get("Content-Type", "")
        assert "application/json" in ct, \
            f"Unexpected Content-Type: {ct}"

    def test_response_time_under_3_seconds(self):
        """Auth endpoint must respond within 3 seconds."""
        resp    = requests.get(AUTH_URL)
        elapsed = resp.elapsed.total_seconds()
        assert elapsed < 3.0, \
            f"Response too slow: {elapsed:.2f}s"

    def test_consecutive_calls_return_unique_keys(self):
        """Two consecutive auth calls should return different API keys."""
        key1 = requests.get(AUTH_URL).json().get("apiKey")
        key2 = requests.get(AUTH_URL).json().get("apiKey")
        assert key1 != key2, \
            "Both auth calls returned identical API keys — possible caching issue"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 2 — POST /accounts  (happy path)
# ══════════════════════════════════════════════════════════════════════════════

class TestPostAccountsHappyPath:
    """Validates successful account creation  POST /api/v1/accounts"""

    def test_create_account_returns_201(self, api_key, account_payload):
        """Valid payload with valid auth must return 201 Created."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert resp.status_code == 201, \
            f"Expected 201, got {resp.status_code} | {resp.text}"

    def test_response_is_valid_json(self, api_key, account_payload):
        """Response body must be valid JSON."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        try:
            resp.json()
        except ValueError:
            pytest.fail("Create account response is not valid JSON")

    def test_response_contains_id(self, api_key, account_payload):
        """Created account must include an 'id' field."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert "id" in resp.json(), \
            f"'id' not found in response: {resp.json()}"

    def test_response_owner_matches_payload(self, api_key, account_payload):
        """Returned owner must exactly match the submitted owner."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert resp.json().get("owner") == account_payload["owner"], \
            f"Owner mismatch: sent '{account_payload['owner']}', got '{resp.json().get('owner')}'"

    def test_response_balance_is_zero(self, api_key, account_payload):
        """Returned balance must match the submitted balance of 0."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert resp.json().get("balance") == 0, \
            f"Balance mismatch: expected 0, got {resp.json().get('balance')}"

    def test_response_currency_is_cosmic_coins(self, api_key, account_payload):
        """Returned currency must be COSMIC_COINS."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert resp.json().get("currency") == VALID_CURRENCY, \
            f"Currency mismatch: got '{resp.json().get('currency')}'"

    def test_id_is_non_empty(self, api_key, account_payload):
        """Account ID must be a non-empty value."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        account_id = resp.json().get("id")
        assert account_id is not None and str(account_id) != "", \
            f"Account ID is empty or None: {account_id}"

    def test_response_time_under_3_seconds(self, api_key, account_payload):
        """POST /accounts must respond within 3 seconds."""
        resp = requests.post(
            ACCOUNTS_URL, json=account_payload, headers=auth_headers(api_key)
        )
        assert resp.elapsed.total_seconds() < 3.0, \
            f"Response too slow: {resp.elapsed.total_seconds():.2f}s"

    def test_multiple_accounts_have_unique_ids(self, api_key):
        """Creating two accounts back-to-back must yield distinct IDs."""
        ids = []
        for _ in range(2):
            payload = {"owner": random_name(), "balance": 0, "currency": VALID_CURRENCY}
            resp    = requests.post(
                ACCOUNTS_URL, json=payload, headers=auth_headers(api_key)
            )
            assert resp.status_code == 201
            ids.append(resp.json().get("id"))
        assert ids[0] != ids[1], \
            f"Duplicate IDs returned: {ids}"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 3 — POST /accounts  (auth & security)
# ══════════════════════════════════════════════════════════════════════════════

class TestPostAccountsAuth:
    """Validates auth enforcement on  POST /api/v1/accounts"""

    def test_no_api_key_returns_401(self, account_payload):
        """Request without auth header must return 401."""
        resp = requests.post(ACCOUNTS_URL, json=account_payload)
        assert resp.status_code == 401, \
            f"Expected 401, got {resp.status_code}"

    def test_invalid_api_key_returns_401(self, account_payload):
        """Request with a fake API key must return 401."""
        resp = requests.post(
            ACCOUNTS_URL,
            json=account_payload,
            headers={"x-api-key": "invalid.fakekey999", "Content-Type": "application/json"},
        )
        assert resp.status_code == 401, \
            f"Expected 401, got {resp.status_code}"

    def test_empty_api_key_returns_401_or_400(self, account_payload):
        """Empty API key string must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json=account_payload,
            headers={"x-api-key": "", "Content-Type": "application/json"},
        )
        assert resp.status_code in (400, 401), \
            f"Expected 400/401, got {resp.status_code}"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 4 — POST /accounts  (validation / edge cases)
# ══════════════════════════════════════════════════════════════════════════════

class TestPostAccountsValidation:
    """Validates input rejection on  POST /api/v1/accounts"""

    def test_missing_owner_field_rejected(self, api_key):
        """Payload without 'owner' must be rejected with 4xx."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"balance": 0, "currency": VALID_CURRENCY},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx, got {resp.status_code}"

    def test_missing_balance_field_rejected(self, api_key):
        """Payload without 'balance' must be rejected with 4xx."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": random_name(), "currency": VALID_CURRENCY},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx, got {resp.status_code}"

    def test_missing_currency_field_rejected(self, api_key):
        """Payload without 'currency' must be rejected with 4xx."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": random_name(), "balance": 0},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx, got {resp.status_code}"

    def test_invalid_currency_rejected(self, api_key):
        """Unknown currency string must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": random_name(), "balance": 0, "currency": "FAKE_COIN"},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx for invalid currency, got {resp.status_code}"

    def test_empty_owner_string_rejected(self, api_key):
        """Empty string for 'owner' must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": "", "balance": 0, "currency": VALID_CURRENCY},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx for empty owner, got {resp.status_code}"

    def test_balance_as_string_rejected(self, api_key):
        """Non-numeric balance must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": random_name(), "balance": "zero", "currency": VALID_CURRENCY},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx for string balance, got {resp.status_code}"

    def test_negative_balance_rejected(self, api_key):
        """Negative balance must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={"owner": random_name(), "balance": -500, "currency": VALID_CURRENCY},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx for negative balance, got {resp.status_code}"

    def test_empty_body_rejected(self, api_key):
        """Completely empty payload must be rejected."""
        resp = requests.post(
            ACCOUNTS_URL,
            json={},
            headers=auth_headers(api_key),
        )
        assert 400 <= resp.status_code < 500, \
            f"Expected 4xx for empty body, got {resp.status_code}"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 5 — GET /accounts/:id
# ══════════════════════════════════════════════════════════════════════════════

class TestGetAccountById:
    """Validates fetching a single account  GET /api/v1/accounts/:id"""

    def test_get_existing_account_returns_200(self, api_key, created_account):
        """Fetching a known account ID must return 200 OK."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 200, \
            f"Expected 200, got {resp.status_code} | {resp.text}"

    def test_response_is_valid_json(self, api_key, created_account):
        """Response body must be valid JSON."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        try:
            resp.json()
        except ValueError:
            pytest.fail("GET /accounts/:id response is not valid JSON")

    def test_returned_id_matches_requested_id(self, api_key, created_account):
        """Returned 'id' must match the requested account ID."""
        account_id = created_account["id"]
        resp = requests.get(
            f"{ACCOUNTS_URL}/{account_id}",
            headers=auth_headers(api_key),
        )
        assert str(resp.json().get("id")) == str(account_id), \
            f"ID mismatch: expected {account_id}, got {resp.json().get('id')}"

    def test_returned_owner_matches(self, api_key, created_account):
        """Returned 'owner' must match the originally created account."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        assert resp.json().get("owner") == created_account["owner"], \
            "Owner mismatch on GET /accounts/:id"

    def test_returned_balance_is_zero(self, api_key, created_account):
        """Returned 'balance' must be 0 (as created)."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        assert resp.json().get("balance") == 0, \
            f"Balance mismatch: expected 0, got {resp.json().get('balance')}"

    def test_returned_currency_is_cosmic_coins(self, api_key, created_account):
        """Returned 'currency' must be COSMIC_COINS."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        assert resp.json().get("currency") == VALID_CURRENCY, \
            f"Currency mismatch on GET /accounts/:id"

    def test_nonexistent_account_returns_404(self, api_key):
        """Fetching a non-existent account ID must return 404."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/nonexistent-id-00000",
            headers=auth_headers(api_key),
        )
        assert resp.status_code == 404, \
            f"Expected 404, got {resp.status_code}"

    def test_get_account_without_auth_returns_401(self, created_account):
        """Request without API key must return 401."""
        resp = requests.get(f"{ACCOUNTS_URL}/{created_account['id']}")
        assert resp.status_code == 401, \
            f"Expected 401, got {resp.status_code}"

    def test_response_time_under_3_seconds(self, api_key, created_account):
        """GET /accounts/:id must respond within 3 seconds."""
        resp = requests.get(
            f"{ACCOUNTS_URL}/{created_account['id']}",
            headers=auth_headers(api_key),
        )
        assert resp.elapsed.total_seconds() < 3.0, \
            f"Response too slow: {resp.elapsed.total_seconds():.2f}s"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 6 — GET /locations
# ══════════════════════════════════════════════════════════════════════════════

class TestGetLocations:
    """
    Validates  GET /api/v1/locations
    Response structure:
      { "space_currencies": [
          { "currency_code": "CC", "currency_name": "COSMIC_COINS",
            "atm_locations": [
              { "planet", "location", "transfersAccepted", "depositsAccepted", "isOpenNow" }
            ]
          }, ...
        ]
      }
    """

    def test_status_code_200(self, api_key):
        """Locations endpoint must return HTTP 200."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert resp.status_code == 200, \
            f"Expected 200, got {resp.status_code}"

    def test_response_is_valid_json(self, api_key):
        """Response body must be valid JSON."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        try:
            resp.json()
        except ValueError:
            pytest.fail("Locations response is not valid JSON")

    def test_response_contains_space_currencies_key(self, api_key):
        """Top-level key 'space_currencies' must be present."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert "space_currencies" in resp.json(), \
            f"'space_currencies' not found: {resp.json()}"

    def test_space_currencies_is_a_list(self, api_key):
        """'space_currencies' must be a list."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert isinstance(resp.json()["space_currencies"], list), \
            "'space_currencies' is not a list"

    def test_space_currencies_has_three_entries(self, api_key):
        """There must be exactly 3 currency entries (CC, MB, GG)."""
        resp       = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        currencies = resp.json()["space_currencies"]
        assert len(currencies) == 3, \
            f"Expected 3 currencies, got {len(currencies)}"

    def test_each_currency_has_required_fields(self, api_key):
        """Every currency object must have currency_code, currency_name, atm_locations."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        for currency in resp.json()["space_currencies"]:
            for field in ("currency_code", "currency_name", "atm_locations"):
                assert field in currency, \
                    f"Field '{field}' missing from currency entry: {currency}"

    def test_currency_codes_are_valid(self, api_key):
        """All returned currency codes must be CC, MB, or GG."""
        resp  = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        codes = [c["currency_code"] for c in resp.json()["space_currencies"]]
        for code in codes:
            assert code in VALID_CURRENCY_CODES, \
                f"Unexpected currency code: {code}"

    def test_currency_names_are_valid(self, api_key):
        """All returned currency names must be known space currencies."""
        resp  = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        names = [c["currency_name"] for c in resp.json()["space_currencies"]]
        for name in names:
            assert name in VALID_CURRENCIES, \
                f"Unexpected currency name: {name}"

    def test_each_currency_has_three_atm_locations(self, api_key):
        """Each currency must have exactly 3 ATM locations."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        for currency in resp.json()["space_currencies"]:
            atms = currency["atm_locations"]
            assert len(atms) == 3, \
                f"{currency['currency_name']} has {len(atms)} ATMs, expected 3"

    def test_atm_locations_have_required_fields(self, api_key):
        """Each ATM entry must have planet, location, transfersAccepted, depositsAccepted, isOpenNow."""
        resp     = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        required = {"planet", "location", "transfersAccepted", "depositsAccepted", "isOpenNow"}
        for currency in resp.json()["space_currencies"]:
            for atm in currency["atm_locations"]:
                missing = required - atm.keys()
                assert not missing, \
                    f"ATM entry missing fields {missing}: {atm}"

    def test_atm_planets_are_from_known_list(self, api_key):
        """All ATM planets must appear in the known planets list."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        for currency in resp.json()["space_currencies"]:
            for atm in currency["atm_locations"]:
                assert atm["planet"] in KNOWN_PLANETS, \
                    f"Unknown planet: '{atm['planet']}'"

    def test_atm_boolean_fields_are_booleans(self, api_key):
        """transfersAccepted, depositsAccepted, isOpenNow must be Python booleans."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        for currency in resp.json()["space_currencies"]:
            for atm in currency["atm_locations"]:
                for field in ("transfersAccepted", "depositsAccepted", "isOpenNow"):
                    assert isinstance(atm[field], bool), \
                        f"Field '{field}' is not boolean in ATM on {atm['planet']}"

    def test_cosmic_coins_atms_on_correct_planets(self, api_key):
        """COSMIC_COINS ATMs must be on Mercury, Mars, and Jupiter."""
        resp   = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        cosmic = next(
            c for c in resp.json()["space_currencies"]
            if c["currency_name"] == "COSMIC_COINS"
        )
        planets = {atm["planet"] for atm in cosmic["atm_locations"]}
        assert {"Mercury", "Mars", "Jupiter"}.issubset(planets), \
            f"COSMIC_COINS planets mismatch: {planets}"

    def test_all_atms_accept_transfers(self, api_key):
        """Every ATM location must have transfersAccepted = True."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        for currency in resp.json()["space_currencies"]:
            for atm in currency["atm_locations"]:
                assert atm["transfersAccepted"] is True, \
                    f"ATM on {atm['planet']} does not accept transfers"

    def test_at_least_one_atm_is_open_now(self, api_key):
        """At least one ATM across all currencies must be open right now."""
        resp     = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        open_atms = [
            atm
            for currency in resp.json()["space_currencies"]
            for atm in currency["atm_locations"]
            if atm["isOpenNow"]
        ]
        assert len(open_atms) > 0, \
            "No ATMs are currently open across any currency"

    def test_locations_response_time_under_3s(self, api_key):
        """GET /locations must respond within 3 seconds."""
        resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert resp.elapsed.total_seconds() < 3.0, \
            f"Response too slow: {resp.elapsed.total_seconds():.2f}s"

    def test_locations_without_auth_returns_401(self):
        """Request without API key must return 401."""
        resp = requests.get(LOCATIONS_URL)
        assert resp.status_code == 401, \
            f"Expected 401, got {resp.status_code}"


# ══════════════════════════════════════════════════════════════════════════════
#  SUITE 7 — End-to-End Integration Flows
# ══════════════════════════════════════════════════════════════════════════════

class TestEndToEndFlow:
    """Full integration flows wiring multiple APIs together."""

    def test_auth_create_then_fetch_account(self):
        """
        E2E Flow A:
          1. GET /auth            → obtain API key
          2. POST /accounts       → create account with balance=0
          3. GET /accounts/:id    → fetch the created account by ID
          4. Validate all fields  → owner, balance, currency, id
        """
        # Step 1 ── Auth
        auth_resp = requests.get(AUTH_URL)
        assert auth_resp.status_code == 200, "Step 1 failed: /auth returned non-200"
        key = auth_resp.json().get("apiKey")
        assert key, "Step 1 failed: No apiKey in response"

        # Step 2 ── Create account
        owner   = random_name()
        payload = {"owner": owner, "balance": 0, "currency": VALID_CURRENCY}
        create_resp = requests.post(
            ACCOUNTS_URL, json=payload, headers=auth_headers(key)
        )
        assert create_resp.status_code == 201, \
            f"Step 2 failed: {create_resp.status_code} | {create_resp.text}"
        account_id = create_resp.json().get("id")
        assert account_id, "Step 2 failed: No 'id' in create response"

        # Step 3 ── Fetch by ID
        fetch_resp = requests.get(
            f"{ACCOUNTS_URL}/{account_id}", headers=auth_headers(key)
        )
        assert fetch_resp.status_code == 200, \
            f"Step 3 failed: {fetch_resp.status_code} | {fetch_resp.text}"

        # Step 4 ── Validate
        fetched = fetch_resp.json()
        assert str(fetched.get("id"))      == str(account_id), "E2E: ID mismatch"
        assert fetched.get("owner")        == owner,           "E2E: Owner mismatch"
        assert fetched.get("balance")      == 0,               "E2E: Balance mismatch"
        assert fetched.get("currency")     == VALID_CURRENCY,  "E2E: Currency mismatch"

    def test_auth_then_fetch_locations(self):
        """
        E2E Flow B:
          1. GET /auth        → obtain API key
          2. GET /locations   → fetch ATM locations
          3. Verify at least one open COSMIC_COINS ATM exists
        """
        # Step 1 ── Auth
        key = requests.get(AUTH_URL).json().get("apiKey")
        assert key, "Auth failed in locations E2E test"

        # Step 2 ── Locations
        loc_resp = requests.get(LOCATIONS_URL, headers=auth_headers(key))
        assert loc_resp.status_code == 200, \
            f"Locations call failed: {loc_resp.status_code}"

        # Step 3 ── Verify open COSMIC_COINS ATM
        cosmic = next(
            (c for c in loc_resp.json()["space_currencies"]
             if c["currency_name"] == VALID_CURRENCY),
            None
        )
        assert cosmic, "COSMIC_COINS not found in /locations"
        open_atms = [atm for atm in cosmic["atm_locations"] if atm["isOpenNow"]]
        assert len(open_atms) > 0, \
            "No open COSMIC_COINS ATMs found — expected at least one"

    def test_account_currency_matches_locations(self, api_key):
        """
        E2E Flow C — Business logic:
          1. POST /accounts  with COSMIC_COINS
          2. GET /locations
          3. Verify the account's currency is listed in /locations
        """
        # Step 1 ── Create account
        payload = {"owner": random_name(), "balance": 0, "currency": VALID_CURRENCY}
        create_resp = requests.post(
            ACCOUNTS_URL, json=payload, headers=auth_headers(api_key)
        )
        assert create_resp.status_code == 201
        used_currency = create_resp.json().get("currency")

        # Step 2 ── Locations
        loc_resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert loc_resp.status_code == 200

        # Step 3 ── Cross-validate
        location_currencies = [
            c["currency_name"] for c in loc_resp.json()["space_currencies"]
        ]
        assert used_currency in location_currencies, \
            f"Account currency '{used_currency}' not found in /locations: {location_currencies}"

    def test_create_account_and_find_nearest_open_atm(self, api_key):
        """
        E2E Flow D — Full business scenario:
          1. POST /accounts  with COSMIC_COINS, balance=0
          2. GET  /locations
          3. Find all open ATMs for COSMIC_COINS
          4. Assert at least one open ATM accepts deposits (for funding the account)
        """
        # Step 1 ── Create account
        payload = {"owner": random_name(), "balance": 0, "currency": VALID_CURRENCY}
        resp    = requests.post(
            ACCOUNTS_URL, json=payload, headers=auth_headers(api_key)
        )
        assert resp.status_code == 201

        # Step 2 ── Locations
        loc_resp = requests.get(LOCATIONS_URL, headers=auth_headers(api_key))
        assert loc_resp.status_code == 200

        # Step 3 & 4 ── Find open deposit-accepting ATMs for COSMIC_COINS
        cosmic = next(
            c for c in loc_resp.json()["space_currencies"]
            if c["currency_name"] == VALID_CURRENCY
        )
        deposit_atms = [
            atm for atm in cosmic["atm_locations"]
            if atm["isOpenNow"] and atm["depositsAccepted"]
        ]
        assert len(deposit_atms) > 0, \
            "No open COSMIC_COINS ATMs accept deposits — cannot fund the new account"