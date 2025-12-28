import requests

url = "https://valentinos-coffee.herokuapp.com/status"
response = requests.get(url)
print(response)
print(response.content)