import requests
import pytest


class TestFootballAPI:
    # Replace with your actual API token
    API_TOKEN = "YOUR_API_TOKEN_HERE"
    BASE_URL = "https://api.football-data.org/v4"

    @pytest.fixture
    def api_headers(self):
        return {"X-Auth-Token": self.API_TOKEN}

    def test_get_competition_teams(self, api_headers):
        """Validate status code and basic structure of the teams endpoint"""
        competition_id = 2021  # Premier League
        endpoint = f"{self.BASE_URL}/competitions/{competition_id}/teams"

        response = requests.get(endpoint, headers=api_headers)
        data = response.json()

        # 1. Validate Status Code
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

        # 2. Validate Competition Details
        assert data["competition"]["code"] == "PL"
        assert data["competition"]["name"] == "Premier League"

        # 3. Validate Teams List
        assert "teams" in data
        assert len(data["teams"]) > 0

        # 4. Check a specific team in the list (e.g., Arsenal)
        team_names = [team["name"] for team in data["teams"]]
        assert "Arsenal FC" in team_names

    def test_api_invalid_token(self):
        """Validate that the API rejects requests without a valid token"""
        endpoint = f"{self.BASE_URL}/competitions/2021/teams"
        invalid_headers = {"X-Auth-Token": "invalid_token_123"}

        response = requests.get(endpoint, headers=invalid_headers)

        # Free tier usually returns 403 or 401 for auth issues
        assert response.status_code in [401, 403]