"""
Configuration loader.
Reads environment variables from .env and exposes them as a config object.
"""
import os
from pathlib import Path


# Load .env file from project root
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    BASE_URL = os.getenv("BASE_URL", "https://rahulshettyacademy.com/oauthapi")
    TOKEN_ENDPOINT = os.getenv("TOKEN_ENDPOINT", "/oauth2/resourceOwner/token")
    COURSE_ENDPOINT = os.getenv("COURSE_ENDPOINT", "/getCourseDetails")

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    GRANT_TYPE = os.getenv("GRANT_TYPE", "client_credentials")
    SCOPE = os.getenv("SCOPE", "trust")

    @classmethod
    def token_url(cls) -> str:
        return f"{cls.BASE_URL}{cls.TOKEN_ENDPOINT}"

    @classmethod
    def course_url(cls) -> str:
        return f"{cls.BASE_URL}{cls.COURSE_ENDPOINT}"
