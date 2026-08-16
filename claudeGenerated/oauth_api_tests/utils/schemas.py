"""
JSON schemas used by tests to validate response shapes.
"""

TOKEN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["access_token", "token_type", "expires_in", "scope"],
    "properties": {
        "access_token": {"type": "string", "minLength": 1},
        "token_type": {"type": "string"},
        "expires_in": {"type": "number", "minimum": 1},
        "scope": {"type": "string"},
    },
}

COURSE_DETAILS_SCHEMA = {
    "type": "object",
    "required": ["courses"],
    "properties": {
        "courses": {
            "type": "object",
            "properties": {
                "webAutomation": {"type": "array"},
                "api": {"type": "array"},
                "mobile": {"type": "array"},
            },
        },
        "instructor": {"type": "string"},
        "linkedIn": {"type": "string"},
        "url": {"type": "string"},
    },
}
