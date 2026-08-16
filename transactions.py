import requests

def test_getAPIKey():
    getkey = requests.get("https://template.postman-echo.com/api/v1/auth")
    response = getkey.json()
    print(response)