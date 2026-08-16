import requests
import pytest


class TestMapsAPI:
    base_url = "https://rahulshettyacademy.com"
    key = "qaclick123"
    place_id = ""  # Global variable to share place_id across tests

    def test_add_place(self):
        """Validate POST API: Adding a new place"""
        endpoint = f"{self.base_url}/maps/api/place/add/json"
        query_params = {"key": self.key}

        payload = {
            "location": {"lat": -38.383494, "lng": 33.427362},
            "accuracy": 50,
            "name": "Garden city",
            "phone_number": "(+91) 983 893 3966",
            "address": "29, side layout, cohen 09",
            "types": ["shoe house", "shop"],
            "website": "http://google.com",
            "language": "French-IN"
        }

        response = requests.post(endpoint, params=query_params, json=payload)
        response_json = response.json()

        # Assertions
        assert response.status_code == 200
        assert response_json["status"] == "OK"
        assert "place_id" in response_json

        # Capture place_id for subsequent tests
        TestMapsAPI.place_id = response_json["place_id"]
        print(f"\nCreated Place ID: {TestMapsAPI.place_id}")

    def test_get_place(self):
        """Validate GET API: Fetching the added place"""
        if not TestMapsAPI.place_id:
            pytest.fail("Place ID was not captured from POST request.")

        endpoint = f"{self.base_url}/maps/api/place/get/json"
        query_params = {
            "key": self.key,
            "place_id": TestMapsAPI.place_id
        }

        response = requests.get(endpoint, params=query_params)
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["name"] == "Garden city"
        assert response_json["address"] == "29, side layout, cohen 09"

    def test_update_place(self):
        """Validate PUT API: Updating the address"""
        if not TestMapsAPI.place_id:
            pytest.fail("Place ID was not captured from POST request.")

        endpoint = f"{self.base_url}/maps/api/place/update/json"
        query_params = {"key": self.key}

        new_address = "22 Summer walk, USA"
        payload = {
            "place_id": TestMapsAPI.place_id,
            "address": new_address,
            "key": self.key
        }

        response = requests.put(endpoint, params=query_params, json=payload)
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["msg"] == "Address successfully updated"

        # Verification: Call GET again to confirm the update
        get_response = requests.get(
            f"{self.base_url}/maps/api/place/get/json",
            params={"key": self.key, "place_id": TestMapsAPI.place_id}
        )
        assert get_response.json()["address"] == new_address