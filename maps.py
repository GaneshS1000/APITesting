import requests
import jsonschema
from jsonschema import validate
from jsonschema.exceptions import ValidationError
#POST Request
postapi_url = "https://rahulshettyacademy.com/maps/api/place/add/json?key=qaclick123"
body = {
  "location": {
    "lat": -38.383494,
    "lng": 33.427362
  },
  "accuracy": 50,
  "name": "Garden city",
  "phone_number": "(+91) 983 893 3966",
  "address": "29, side layout, cohen 09",
  "types": [
    "shoe house",
    "shop"
  ],
  "website": "http://google.com",
  "language": "French-IN"
}
postResponse = requests.post(postapi_url,json=body)
print(postResponse.json())
resp = postResponse.json()
placeId = resp["place_id"]
print("Place ID:",placeId)

schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Generated schema for Root",
  "type": "object",
  "properties": {
    "location": {
      "type": "object",
      "properties": {
        "latitude": {
          "type": "string"
        },
        "longitude": {
          "type": "string"
        }
      },
      "required": [
        "latitude",
        "longitude"
      ]
    },
    "accuracy": {
      "type": "string"
    },
    "name": {
      "type": "string"
    },
    "phone_number": {
      "type": "string"
    },
    "address": {
      "type": "string"
    },
    "types": {
      "type": "string"
    },
    "website": {
      "type": "string"
    },
    "language": {
      "type": "string"
    }
  },
  "required": [
    "location",
    "accuracy",
    "name",
    "phone_number",
    "address",
    "types",
    "website",
    "language"
  ]
}
#GET Request
getApi_url = f"https://rahulshettyacademy.com/maps/api/place/get/json?key=qaclick123&place_id={placeId}"
print(getApi_url)
getResponse = requests.get(getApi_url)
data = getResponse.json()
print(data)
print(type(data))
assert getResponse.status_code == 200
assert data["name"] == "Garden city"
validate(instance=data,schema=schema)

