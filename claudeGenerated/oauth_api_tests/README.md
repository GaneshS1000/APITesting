# OAuth API Test Framework (pytest + requests)

Automated API tests for the `ClientCredentialsOAuth` Postman collection, ported to Python using **pytest** and **requests**.

> **Why not Selenium?** Selenium drives a browser — it's not designed for REST API testing. For HTTP endpoints, `requests` is the standard Python library. The pytest framework, fixtures, reporting, and parameterization patterns shown here are all the same techniques you would use in a Selenium suite.

## Project structure

```
oauth_api_tests/
├── .env                       # Credentials (never commit real secrets)
├── pytest.ini                 # Pytest configuration & markers
├── requirements.txt
├── conftest.py                # Shared fixtures (session-scoped token)
├── config/
│   └── config.py              # Loads .env → Config class
├── utils/
│   ├── api_client.py          # OAuthAPIClient wrapping requests
│   └── schemas.py             # JSON schemas for validation
├── tests/
│   ├── test_authorization_server.py
│   └── test_get_course_details.py
└── reports/
    └── report.html            # Generated after a run
```

## Setup

```bash
pip install -r requirements.txt
```

## Run all tests

```bash
pytest
```

## Run by marker

```bash
pytest -m smoke         # quick sanity checks
pytest -m positive      # only positive tests
pytest -m negative      # only error-path tests
pytest -m e2e           # end-to-end flow
```

## Run a single file or test

```bash
pytest tests/test_authorization_server.py
pytest tests/test_authorization_server.py::TestAuthorizationServerPositive::test_token_request_returns_200
```

## Parallel execution

```bash
pytest -n 4             # 4 workers (pytest-xdist)
```

## HTML report

After any run, open `reports/report.html`.

## Security note

The `.env` file contains the client secret from your Postman collection. **Rotate it** if it's a real credential, and add `.env` to `.gitignore` before committing.
