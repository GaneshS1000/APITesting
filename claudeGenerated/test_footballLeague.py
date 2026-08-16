import os
import re
import time
from urllib.parse import urlparse

import pytest
import requests

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
BASE_URL = "https://api.football-data.org/v4"
API_TOKEN = os.getenv("FOOTBALL_API_TOKEN", "476241048d064252a8c68f3e31951a1b")
COMPETITION_ID = 2021  # Premier League
ENDPOINT = f"{BASE_URL}/competitions/{COMPETITION_ID}/teams"

VALID_HEADERS = {"X-Auth-Token": API_TOKEN}
TIMEOUT = 10  # seconds per request


# ──────────────────────────────────────────────
# Shared fixtures
# ──────────────────────────────────────────────
@pytest.fixture(scope="module")
def valid_response():
    """Single authenticated GET – reused across the whole module."""
    resp = requests.get(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
    assert resp.status_code == 200, (
        f"Fixture setup failed – expected 200, got {resp.status_code}. "
        "Check that FOOTBALL_API_TOKEN is set correctly."
    )
    return resp


@pytest.fixture(scope="module")
def response_data(valid_response):
    return valid_response.json()


@pytest.fixture(scope="module")
def teams(response_data):
    return response_data["teams"]


# ──────────────────────────────────────────────
# 1. Authentication
# ──────────────────────────────────────────────
class TestAuthentication:

    def test_valid_token_returns_200(self):
        """TC-AUTH-01 : Valid API token → 200 OK."""
        resp = requests.get(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 200

    def test_missing_token_returns_403(self):
        """TC-AUTH-02 : No token → 403 Forbidden."""
        resp = requests.get(ENDPOINT, timeout=TIMEOUT)
        assert resp.status_code == 403

    def test_invalid_token_returns_4xx(self):
        """TC-AUTH-03 : Wrong token → 400 or 403."""
        resp = requests.get(
            ENDPOINT,
            headers={"X-Auth-Token": "invalid_token_xyz_000"},
            timeout=TIMEOUT,
        )
        assert resp.status_code in (400, 403)

    def test_response_body_has_error_message_on_403(self):
        """TC-AUTH-04 : 403 response body contains an error message."""
        resp = requests.get(ENDPOINT, timeout=TIMEOUT)
        body = resp.json()
        assert "message" in body or "error" in body or "detail" in body


# ──────────────────────────────────────────────
# 2. Response Structure
# ──────────────────────────────────────────────
class TestResponseStructure:

    def test_content_type_is_json(self, valid_response):
        """TC-STRUCT-01 : Content-Type header is application/json."""
        assert "application/json" in valid_response.headers.get("Content-Type", "")

    def test_top_level_count_field_exists(self, response_data):
        """TC-STRUCT-02 : Top-level 'count' key is present."""
        assert "count" in response_data

    def test_top_level_filters_is_dict(self, response_data):
        """TC-STRUCT-03 : Top-level 'filters' is a dict."""
        assert isinstance(response_data.get("filters"), dict)

    def test_top_level_competition_is_dict(self, response_data):
        """TC-STRUCT-04 : Top-level 'competition' is a dict."""
        assert isinstance(response_data.get("competition"), dict)

    def test_competition_has_required_keys(self, response_data):
        """TC-STRUCT-05 : 'competition' contains id, name, code, type."""
        comp = response_data["competition"]
        for key in ("id", "name", "code", "type"):
            assert key in comp, f"Missing key in competition: {key}"

    def test_top_level_season_is_dict(self, response_data):
        """TC-STRUCT-06 : Top-level 'season' is a dict."""
        assert isinstance(response_data.get("season"), dict)

    def test_season_has_required_keys(self, response_data):
        """TC-STRUCT-07 : 'season' contains id, startDate, endDate."""
        season = response_data["season"]
        for key in ("id", "startDate", "endDate"):
            assert key in season, f"Missing key in season: {key}"

    def test_top_level_teams_is_list(self, response_data):
        """TC-STRUCT-08 : Top-level 'teams' is a list."""
        assert isinstance(response_data.get("teams"), list)


# ──────────────────────────────────────────────
# 3. Competition & Season Data Correctness
# ──────────────────────────────────────────────
class TestCompetitionData:
    ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def test_competition_id_matches_request(self, response_data):
        """TC-COMP-01 : competition.id == 2021."""
        assert response_data["competition"]["id"] == COMPETITION_ID

    def test_competition_code_is_pl(self, response_data):
        """TC-COMP-02 : competition.code == 'PL'."""
        assert response_data["competition"]["code"] == "PL"

    def test_competition_type_is_league(self, response_data):
        """TC-COMP-03 : competition.type == 'LEAGUE'."""
        assert response_data["competition"]["type"] == "LEAGUE"

    def test_season_start_date_format(self, response_data):
        """TC-COMP-04 : season.startDate is a valid YYYY-MM-DD string."""
        assert self.ISO_DATE.match(response_data["season"]["startDate"])

    def test_season_end_date_format(self, response_data):
        """TC-COMP-05 : season.endDate is a valid YYYY-MM-DD string."""
        assert self.ISO_DATE.match(response_data["season"]["endDate"])

    def test_season_end_date_after_start_date(self, response_data):
        """TC-COMP-06 : endDate > startDate."""
        assert response_data["season"]["endDate"] > response_data["season"]["startDate"]

    def test_competition_name_is_not_empty(self, response_data):
        """TC-COMP-07 : competition.name is a non-empty string."""
        name = response_data["competition"].get("name", "")
        assert isinstance(name, str) and name.strip()


# ──────────────────────────────────────────────
# 4. Teams Array Validation
# ──────────────────────────────────────────────
class TestTeamsArray:
    ISO_8601 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    REQUIRED_KEYS = ("id", "name", "shortName", "tla", "crest")

    def test_teams_array_is_non_empty(self, teams):
        """TC-TEAMS-01 : teams list has at least one entry."""
        assert len(teams) > 0

    def test_premier_league_has_20_teams(self, teams):
        """TC-TEAMS-02 : Premier League always has exactly 20 teams."""
        assert len(teams) == 20

    def test_count_matches_teams_length(self, response_data):
        """TC-TEAMS-03 : 'count' equals len(teams)."""
        assert response_data["count"] == len(response_data["teams"])

    @pytest.mark.parametrize("key", ("id", "name", "shortName", "tla", "crest"))
    def test_each_team_has_required_key(self, teams, key):
        """TC-TEAMS-04 : Every team object contains the required key."""
        missing = [t.get("name", t.get("id")) for t in teams if key not in t]
        assert not missing, f"Teams missing '{key}': {missing}"

    def test_team_ids_are_positive_integers(self, teams):
        """TC-TEAMS-05 : team.id is a positive int for every team."""
        for team in teams:
            assert isinstance(team["id"], int) and team["id"] > 0, (
                f"Invalid id for team: {team}"
            )

    def test_team_tla_is_3_characters(self, teams):
        """TC-TEAMS-06 : team.tla is exactly 3 characters long."""
        for team in teams:
            assert isinstance(team["tla"], str) and len(team["tla"]) == 3, (
                f"Invalid TLA '{team['tla']}' for {team['name']}"
            )

    def test_team_crest_is_valid_url(self, teams):
        """TC-TEAMS-07 : team.crest is a valid URL with http/https scheme."""
        for team in teams:
            parsed = urlparse(team["crest"])
            assert parsed.scheme in ("http", "https") and parsed.netloc, (
                f"Invalid crest URL for {team['name']}: {team['crest']}"
            )

    def test_team_ids_are_unique(self, teams):
        """TC-TEAMS-08 : No duplicate team IDs."""
        ids = [t["id"] for t in teams]
        assert len(ids) == len(set(ids)), "Duplicate team IDs found"

    def test_team_names_are_non_empty_strings(self, teams):
        """TC-TEAMS-09 : team.name is a non-empty string."""
        for team in teams:
            assert isinstance(team["name"], str) and team["name"].strip(), (
                f"Empty name for team id={team['id']}"
            )

    def test_team_address_is_string_or_none(self, teams):
        """TC-TEAMS-10 : team.address is str or None."""
        for team in teams:
            assert team.get("address") is None or isinstance(team["address"], str), (
                f"Unexpected type for address in {team['name']}"
            )

    def test_team_founded_is_int_or_none(self, teams):
        """TC-TEAMS-11 : team.founded is an int or None."""
        for team in teams:
            val = team.get("founded")
            assert val is None or isinstance(val, int), (
                f"Unexpected type for founded in {team['name']}: {val}"
            )

    def test_team_venue_is_string_or_none(self, teams):
        """TC-TEAMS-12 : team.venue is str or None."""
        for team in teams:
            val = team.get("venue")
            assert val is None or isinstance(val, str), (
                f"Unexpected type for venue in {team['name']}: {val}"
            )

    def test_team_last_updated_iso8601(self, teams):
        """TC-TEAMS-13 : team.lastUpdated matches ISO 8601 format."""
        for team in teams:
            assert self.ISO_8601.match(team.get("lastUpdated", "")), (
                f"Invalid lastUpdated for {team['name']}: {team.get('lastUpdated')}"
            )

    def test_team_website_is_url_or_none(self, teams):
        """TC-TEAMS-14 : team.website (if present) is a valid URL or None."""
        for team in teams:
            website = team.get("website")
            if website is not None:
                parsed = urlparse(website)
                assert parsed.scheme in ("http", "https") and parsed.netloc, (
                    f"Invalid website for {team['name']}: {website}"
                )


# ──────────────────────────────────────────────
# 5. Season Filter  (?season=YYYY)
# ──────────────────────────────────────────────
class TestSeasonFilter:

    def test_valid_historical_season_returns_200(self):
        """TC-SEASON-01 : ?season=2020 returns 200."""
        resp = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 2020}, timeout=TIMEOUT
        )
        assert resp.status_code == 200

    def test_historical_season_returns_list_of_teams(self):
        """TC-SEASON-02 : ?season=2020 body contains a non-empty teams list."""
        resp = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 2020}, timeout=TIMEOUT
        )
        data = resp.json()
        assert isinstance(data.get("teams"), list) and len(data["teams"]) > 0

    def test_filters_reflect_requested_season(self):
        """TC-SEASON-03 : filters.season echoes back the requested year."""
        resp = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 2020}, timeout=TIMEOUT
        )
        assert resp.json()["filters"].get("season") == "2020"

    def test_nonexistent_season_returns_4xx(self):
        """TC-SEASON-04 : ?season=1800 (nonexistent) returns a 4xx error."""
        resp = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 1800}, timeout=TIMEOUT
        )
        assert 400 <= resp.status_code < 500

    def test_non_numeric_season_returns_4xx(self):
        """TC-SEASON-05 : ?season=abcd returns a 4xx error."""
        resp = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": "abcd"}, timeout=TIMEOUT
        )
        assert 400 <= resp.status_code < 500

    def test_different_seasons_return_different_season_ids(self):
        """TC-SEASON-06 : Season IDs differ between 2019 and 2022."""
        r1 = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 2019}, timeout=TIMEOUT
        )
        r2 = requests.get(
            ENDPOINT, headers=VALID_HEADERS, params={"season": 2022}, timeout=TIMEOUT
        )
        assert r1.json()["season"]["id"] != r2.json()["season"]["id"]


# ──────────────────────────────────────────────
# 6. Invalid / Edge-case Competition IDs
# ──────────────────────────────────────────────
class TestInvalidCompetitionIDs:

    def test_nonexistent_competition_id_returns_404(self):
        """TC-ERR-01 : Competition ID 9999999 → 404."""
        resp = requests.get(
            f"{BASE_URL}/competitions/9999999/teams",
            headers=VALID_HEADERS,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 404

    def test_non_numeric_competition_id_returns_4xx(self):
        """TC-ERR-02 : Competition ID 'abc' → 4xx."""
        resp = requests.get(
            f"{BASE_URL}/competitions/abc/teams",
            headers=VALID_HEADERS,
            timeout=TIMEOUT,
        )
        assert 400 <= resp.status_code < 500

    def test_negative_competition_id_returns_4xx(self):
        """TC-ERR-03 : Competition ID -1 → 4xx."""
        resp = requests.get(
            f"{BASE_URL}/competitions/-1/teams",
            headers=VALID_HEADERS,
            timeout=TIMEOUT,
        )
        assert 400 <= resp.status_code < 500

    def test_zero_competition_id_returns_4xx(self):
        """TC-ERR-04 : Competition ID 0 → 4xx."""
        resp = requests.get(
            f"{BASE_URL}/competitions/0/teams",
            headers=VALID_HEADERS,
            timeout=TIMEOUT,
        )
        assert 400 <= resp.status_code < 500


# ──────────────────────────────────────────────
# 7. HTTP Method Validation
# ──────────────────────────────────────────────
class TestHTTPMethods:

    def test_post_method_not_allowed(self):
        """TC-HTTP-01 : POST → 405 Method Not Allowed."""
        resp = requests.post(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 405

    def test_put_method_not_allowed(self):
        """TC-HTTP-02 : PUT → 405 Method Not Allowed."""
        resp = requests.put(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 405

    def test_delete_method_not_allowed(self):
        """TC-HTTP-03 : DELETE → 405 Method Not Allowed."""
        resp = requests.delete(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 405

    def test_patch_method_not_allowed(self):
        """TC-HTTP-04 : PATCH → 405 Method Not Allowed."""
        resp = requests.patch(ENDPOINT, headers=VALID_HEADERS, timeout=TIMEOUT)
        assert resp.status_code == 405


# ──────────────────────────────────────────────
# 8. Response Headers
# ──────────────────────────────────────────────
class TestResponseHeaders:

    def test_content_type_header_present(self, valid_response):
        """TC-HDR-01 : Content-Type header is present."""
        assert "Content-Type" in valid_response.headers

    def test_rate_limit_or_auth_header_present(self, valid_response):
        """TC-HDR-02 : At least one rate-limit / auth header is present."""
        rate_headers = {k.lower() for k in valid_response.headers}
        relevant = {
            "x-requests-available-minute",
            "x-requestcounter-reset",
            "x-auth-token-expiration",
            "x-authenticated-client",
        }
        assert relevant & rate_headers, (
            "No rate-limit or auth headers found in response"
        )

    def test_response_is_not_empty(self, valid_response):
        """TC-HDR-03 : Response body is not empty."""
        assert len(valid_response.content) > 0