"""
Test cases for the GetCourseDetails endpoint (protected resource).
Mirrors the Postman 'GetCourseDetails' request.
"""
import pytest
from jsonschema import validate
from utils.schemas import COURSE_DETAILS_SCHEMA


# ====================================================
# POSITIVE TESTS
# ====================================================
@pytest.mark.positive
@pytest.mark.smoke
class TestGetCourseDetailsPositive:
    """Happy-path scenarios for fetching course details with a valid token."""

    def test_request_returns_200(self, api_client, access_token):
        response = api_client.get_course_details(access_token)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_response_time_under_5_seconds(self, api_client, access_token):
        response = api_client.get_course_details(access_token)
        assert response.elapsed.total_seconds() < 5

    def test_response_is_json(self, api_client, access_token):
        response = api_client.get_course_details(access_token)
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_response_matches_schema(self, api_client, access_token):
        response = api_client.get_course_details(access_token)
        validate(instance=response.json(), schema=COURSE_DETAILS_SCHEMA)

    def test_courses_object_present(self, api_client, access_token):
        body = api_client.get_course_details(access_token).json()
        assert "courses" in body
        assert isinstance(body["courses"], dict)

    @pytest.mark.parametrize("category", ["webAutomation", "api", "mobile"])
    def test_course_category_is_list(self, api_client, access_token, category):
        body = api_client.get_course_details(access_token).json()
        assert category in body["courses"], f"Missing category: {category}"
        assert isinstance(body["courses"][category], list)

    def test_web_automation_courses_not_empty(self, api_client, access_token):
        body = api_client.get_course_details(access_token).json()
        assert len(body["courses"]["webAutomation"]) > 0

    def test_each_course_has_required_fields(self, api_client, access_token):
        body = api_client.get_course_details(access_token).json()
        for category, course_list in body["courses"].items():
            for course in course_list:
                assert "courseTitle" in course, (
                    f"Missing courseTitle in {category}: {course}"
                )
                assert "price" in course, f"Missing price in {category}: {course}"
                assert isinstance(course["courseTitle"], str) and course["courseTitle"]

    def test_instructor_when_present_is_rahul_shetty(self, api_client, access_token):
        body = api_client.get_course_details(access_token).json()
        for course_list in body["courses"].values():
            for course in course_list:
                if "instructor" in course:
                    assert course["instructor"] == "Rahul Shetty"


# ====================================================
# NEGATIVE TESTS
# ====================================================
@pytest.mark.negative
class TestGetCourseDetailsNegative:
    """Error-path scenarios — invalid or missing tokens."""

    def test_invalid_token_is_rejected(self, api_client):
        response = api_client.get_course_details(access_token="invalid_token_xyz")
        assert response.status_code in (401, 403), (
            f"Expected 401/403 for invalid token, got {response.status_code}"
        )

    def test_missing_token_is_rejected(self, api_client):
        response = api_client.get_course_details(include_token=False)
        assert response.status_code in (401, 403), (
            f"Expected 401/403 with no token, got {response.status_code}"
        )

    def test_empty_token_is_rejected(self, api_client):
        response = api_client.get_course_details(access_token="")
        assert response.status_code in (401, 403)

    def test_expired_or_malformed_token_is_rejected(self, api_client):
        # Realistic-looking but invalid token
        fake = "eyJhbGciOiJIUzI1NiJ9.invalid.signature"
        response = api_client.get_course_details(access_token=fake)
        assert response.status_code in (401, 403)


# ====================================================
# END-TO-END FLOW
# ====================================================
@pytest.mark.e2e
class TestEndToEndFlow:
    """Verifies the full token → resource access flow in one test."""

    def test_full_oauth_flow(self, api_client):
        # Step 1: get token
        token_resp = api_client.get_access_token()
        assert token_resp.status_code == 200
        token = token_resp.json()["access_token"]

        # Step 2: use token to access protected resource
        course_resp = api_client.get_course_details(token)
        assert course_resp.status_code == 200
        assert "courses" in course_resp.json()
