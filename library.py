#program to test for the library API

import requests

addBook = requests.post("http://216.10.245.166/Library/Addbook.php",json={"name":"Fire And Ice","isbn":"UK151","aisle":"128","author":"George Martin"})
print("Add Book Status Code:",addBook.status_code)
print(addBook.text)
print(addBook.headers)
print(addBook.json())
getBookDetails = requests.get("http://216.10.245.166/Library/GetBook.php?ID=UK151128")
print(getBookDetails.json())
deleteBook = requests.post("http://216.10.245.166/Library/DeleteBook.php",json={"ID":"UK151128"})
print("Delete Book Status Code:",deleteBook.status_code)
print(deleteBook.json())