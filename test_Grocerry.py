import traceback

import requests
import pytest
from jsonschema import validate , ValidationError
from pytest_csv_params.decorator import csv_params
from Grocerry import registerClient,listProducts,creatingCart,addingItem,viewCartItems,orderedCartItems
import json
accessToken = None
cartId = None
orderId = None


@pytest.fixture
def getProductSchema():
    productSchema = "C:\\Users\\Ganesh S\\PycharmProjects\\Testing\\APITesting\\schemaFiles\\productSchema.json"
    schemaFile = open(productSchema,"r")
    schemadata = json.loads(schemaFile.read())
    return schemadata

@pytest.fixture
def getCartSchema():
    cartSchema = "C:\\Users\\Ganesh S\\PycharmProjects\\Testing\\APITesting\\schemaFiles\\cartSchema.json"
    schemaFile = open(cartSchema,"r")
    schemaData = json.loads(schemaFile.read())
    return schemaData


def test_RegisterClient(registerClient):
    try:
        global accessToken
        if accessToken == None:
            accessToken = registerClient
            return accessToken
        else:
            return accessToken
    except:
        traceback.print_exc()


def test_getProductList(getProductSchema):
    products = requests.get("https://simple-grocery-store-api.glitch.me/products")
    assert products.status_code >= 200 and products.status_code < 300
    product_list = products.json()
    try:
        validate(instance=product_list, schema=getProductSchema)
    except ValidationError as e:
        print(e.args)
        exit(-1)
    print(product_list)

def test_createCart(getCartSchema):
    cart = requests.post("https://simple-grocery-store-api.glitch.me/carts")
    assert cart.status_code>=200 and cart.status_code<300
    cart_created = cart.json()
    cartId = cart_created['cartId']
    try:
        validate(instance=cart_created, schema=getCartSchema)
    except ValidationError as e:
        print(e.args)
        exit(-1)
    print(cartId)

def test_addingItem(creatingCart):
    try:
        itemAdd = requests.post(f"https://simple-grocery-store-api.glitch.me/carts/{creatingCart}/items",
                                json={"productId": 4643})
        print("creating cart:",creatingCart)
        print(itemAdd.status_code)
        assert itemAdd.status_code >= 200 and itemAdd.status_code <= 300
        itemAddedResponse = itemAdd.json()
    except AssertionError as e:
        print(e.args)
        itemAddedResponse = itemAdd.json()
        print(itemAddedResponse['error'])
        pytest.fail("Assertion Error")
    except:
        traceback.print_exc()
        pytest.fail("Exception occured")
    print(itemAddedResponse)
    viewCart = requests.get(f"https://simple-grocery-store-api.glitch.me/carts/{creatingCart}/items")
    assert viewCart.status_code == 200
    viewCartResponse = viewCart.json()
    print(viewCartResponse)
    itemId = viewCartResponse[0]['id']
    print(itemId)

def test_orderedCartItems(registerClient,addingItem):
    try:
        headerInfo = {"Authorization": f"Bearer {registerClient}",
                      "Accept": "application/json"}
        print(headerInfo)
        print("Order Cart Items:")
        print("creating cart:",addingItem)
        orderCartItems = requests.post("https://simple-grocery-store-api.click/orders",
                                       json={"cartId": addingItem, "customerName": "Kane"}, headers=headerInfo)
        assert orderCartItems.status_code>=200 and orderCartItems.status_code<300
        orderCartResponse = orderCartItems.json()
        print(orderCartResponse)
        orderId = orderCartResponse['orderId']
        print("Order ID:", orderId)
        print("View Orders:")
        viewOrders = requests.get(f"https://simple-grocery-store-api.click/orders/{ orderId }", headers=headerInfo)
        assert viewOrders.status_code>=200 and viewOrders.status_code<300
        viewOrderResponse = viewOrders.json()
        customerName = viewOrderResponse['customerName']
        assert customerName == "Kane"

        print(viewOrderResponse)
    except AssertionError as e:
        print(e.args)
        pytest.fail("Assertion Error")
    except:
        traceback.print_exc()
        pytest.fail("Exception occured")

