import pytest
import requests


@pytest.fixture
def get_API_Key():
    get_api_key = requests.get("https://template.postman-echo.com/api/v1/auth")
    api_key_respose = get_api_key.json()
    api_key = api_key_respose["apiKey"]
    return api_key

@pytest.fixture
def header_info(get_API_Key):
    headerInfo = {
        "api-key": get_API_Key,
        "Content-Type": "application/json"
    }
    return headerInfo
@pytest.fixture
def test_create_from_account(header_info):
    fromPayload = {
        "owner": "Jim",
        "balance": 50,
        "currency": "COSMIC_COINS"
    }
    create_from_user = requests.post("https://template.postman-echo.com/api/v1/accounts",json=fromPayload,headers=header_info)
    from_user_response = create_from_user.json()
    from_user_id = from_user_response["account"]["id"]
    assert create_from_user.status_code==200
    return from_user_id

@pytest.fixture
def test_create_to_account(header_info):
    toPayload = {
        "owner": "Tim",
        "balance": 10,
        "currency": "COSMIC_COINS"
    }
    create_to_user = requests.post("https://template.postman-echo.com/api/v1/accounts",json=toPayload,headers=header_info)
    to_user_response = create_to_user.json()
    to_user_id = to_user_response["account"]["id"]
    assert create_to_user.status_code==200
    return to_user_id

def test_get_user_accounts(header_info):
    get_user_accounts = requests.get("https://template.postman-echo.com/api/v1/accounts",headers=header_info)
    user_accounts_response = get_user_accounts.json()
    print(user_accounts_response)
    assert get_user_accounts.status_code == 200

def test_create_transaction(header_info,test_create_from_account,test_create_to_account):
    transaction_payload = {
        "fromAccountId":test_create_from_account,
        "toAccountId":test_create_to_account,
        "amount":100,
        "currency": "COSMIC_COINS"
    }
    create_transaction = requests.post("https://template.postman-echo.com/api/v1/transactions",json=transaction_payload,headers=header_info)
    transaction_response = create_transaction.json()
    print(transaction_response)



