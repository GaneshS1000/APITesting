import requests

get_api_key = requests.get("https://template.postman-echo.com/api/v1/auth")
apikey_response = get_api_key.json()
api_key = apikey_response['apiKey']
print(api_key)
headerInfo = {
    "api-key":api_key,
    "Content-Type": "application/json"
}
fromPayload = {
    "owner": "Jim",
    "balance": 50,
    "currency": "COSMIC_COINS"
}
createFromUser = requests.post("https://template.postman-echo.com/api/v1/accounts",json=fromPayload,headers=headerInfo)
fromUserResponse = createFromUser.json()
print(fromUserResponse)
fromAccountId = fromUserResponse['account']['id']
toPayload = {
    "owner": "Jam",
    "balance": 0,
    "currency": "COSMIC_COINS"
}
createToUser = requests.post("https://template.postman-echo.com/api/v1/accounts", json=toPayload, headers=headerInfo)
toUserresponse = createToUser.json()
print(toUserresponse)
toAccountId = toUserresponse['account']['id']
user_accounts = requests.get("https://template.postman-echo.com/api/v1/accounts",headers=headerInfo)
user_accounts_response = user_accounts.json()
print(user_accounts_response)

