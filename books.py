import requests

#Get Request
getAPI_url = "https://restful-booker.herokuapp.com/booking"
print("URL :")
print(getAPI_url)
print("Json Response:")
response = requests.get(getAPI_url)
print(response.json())
print("Status Code:",response.status_code)
assert response.status_code == 200
print("Content:")
print(response.content)
print("Cookies:")
print(response.cookies.values())