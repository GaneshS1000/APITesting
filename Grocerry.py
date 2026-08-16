#program to test for Grocerry APIs
import json
import requests
import logging
import http.client as http_client
from jsonschema import validate , ValidationError
import pytest
from pytest_csv_params.decorator import csv_params
'''
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''

validate_ProductSchema = "C:\\Users\\Ganesh S\\PycharmProjects\\Testing\\APITesting\\schemaFiles\\productSchema.json"
validate_CartSchema = "C:\\Users\\Ganesh S\\PycharmProjects\\Testing\\APITesting\\schemaFiles\\cartSchema.json"
accessToken = None

#Register Client
@pytest.fixture
def registerClient():
  global accessToken
  if accessToken == None:
    csvData = open(r"C:\Users\Ganesh S\PycharmProjects\Testing\APITesting\csvFiles\client.csv","r")
    data = csvData.readlines()
    clientDet = data[1].strip("\n").split(",")
    print(clientDet)
    clientName = clientDet[1]
    clientEmail = clientDet[2]
    registerClient = requests.post("https://simple-grocery-store-api.glitch.me/api-clients",json={"clientName":clientName,"clientEmail":clientEmail})
    registerResponse = registerClient.json()
    print(registerResponse)
    accessToken = registerResponse["accessToken"]
  return accessToken



def listProducts(getProductSchema):
  products = requests.get("https://simple-grocery-store-api.glitch.me/products")
  product_list = products.json()
  try:
    validate(instance=product_list,schema=getProductSchema)
  except ValidationError as e:
    print(e.args)
    exit(-1)
  return product_list

@pytest.fixture
def creatingCart(getCartSchema):
  cart = requests.post("https://simple-grocery-store-api.glitch.me/carts")
  assert cart.status_code>=200 and cart.status_code<300
  cart_created = cart.json()
  cartId = cart_created['cartId']
  return cartId

@pytest.fixture
def addingItem(creatingCart):
  itemAdd = requests.post(f"https://simple-grocery-store-api.glitch.me/carts/{creatingCart}/items",json={"productId":4643})
  print(itemAdd.status_code)
  assert itemAdd.status_code>= 200 and itemAdd.status_code<=300
  itemAddedResponse = itemAdd.json()
  itemId = itemAddedResponse['itemId']
  return creatingCart


def viewCartItems(creatingCart):
  viewCart = requests.get(f"https://simple-grocery-store-api.glitch.me/carts/{creatingCart}/items")
  assert viewCart.status_code == 200
  viewCartResponse = viewCart.json()
  print(viewCartResponse)
  itemId = viewCartResponse['itemId']
  return itemId

@pytest.fixture
def orderedCartItems(registerClient,creatingCart):
  headerInfo = {"Authorization": f"Bearer {registerClient}",
             "Accept": "application/json"}
  print(headerInfo)
  print("Order Cart Items:")
  orderCartItems = requests.post("https://simple-grocery-store-api.click/orders",json={"cartId":creatingCart,"customerName":"Kane"},headers=headerInfo)
  assert orderCartItems.status_code>=200 and orderCartItems.status_code<300
  orderCartResponse = orderCartItems.json()
  print(orderCartResponse)
  orderId = orderCartResponse['orderId']
  print("Order ID:",orderId)
  viewOrders = requests.get(f"https://simple-grocery-store-api.click/orders/{orderId}",headers=headerInfo)
  assert viewOrders.status_code>=200 and viewOrders.status_code<300
  viewOrderResponse = viewOrders.json()
  return viewOrderResponse

