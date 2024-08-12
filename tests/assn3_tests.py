import pytest
import requests

BASE_URL = "http://localhost:5001"
BOOK2_ID = 0

# Test data
book1 = { "title":"Adventures of Huckleberry Finn", "ISBN":"9780520343641", "genre":"Fiction" }
book2 = { "title":"The Best of Isaac Asimov", "ISBN":"9780385050784", "genre":"Science Fiction"}
book3 = { "title":"Fear No Evil", "ISBN":"9780394558783", "genre":"Biography" }
book4 = { "title": "No such book", "ISBN":"0000001111111", "genre":"Biography" }
book5 = { "title":"The Greatest Joke Book Ever", "authors":"Mel Greene", "ISBN":"9780380798490", "genre":"Jokes" }
Book6 = { "title":"The Adventures of Tom Sawyer", "ISBN":"9780195810400", "genre":"Fiction" }
book7 = { "title": "I, Robot", "ISBN":"9780553294385", "genre":"Science Fiction"}
book8 = { "title": "Second Foundation", "ISBN":"9780553293364", "genre":"Science Fiction"}

def test_post_books():
    response1 = requests.post(f"{BASE_URL}/books", json=book1)
    assert response1.status_code == 201

    response2 = requests.post(f"{BASE_URL}/books", json=book2)
    assert response2.status_code == 201

    response3 = requests.post(f"{BASE_URL}/books", json=book3)
    assert response3.status_code == 201

    id1 = requests.get(f"{BASE_URL}/books").json()[0].get("id")
    assert id1 is not None

    BOOK2_ID = requests.get(f"{BASE_URL}/books").json()[1].get("id")
    assert BOOK2_ID is not None

    id3 = requests.get(f"{BASE_URL}/books").json()[2].get("id")
    assert id3 is not None

    assert id1 != BOOK2_ID
    assert id1 != id3
    assert BOOK2_ID != id3

def test_get_book_by_id():
    book_id = requests.get(f"{BASE_URL}/books").json()[0].get("id")

    response = requests.get(f"{BASE_URL}/books/{book_id}")
    assert response.status_code == 200
    
    book_data = response.json()
    assert book_data["authors"] == "Mark Twain"

def test_get_all_books():
    response = requests.get(f"{BASE_URL}/books")
    assert response.status_code == 200

    books = response.json()
    assert len(books) == 3

def test_wrong_ISBN():
    response = requests.post(f"{BASE_URL}/books", json=book4)
    assert (response.status_code == 400 or response.status_code == 500)

def test_delete_book():
    response = requests.delete(f"{BASE_URL}/books/{BOOK2_ID}")
    assert response.status_code == 200

def test_get_book_by_ID():
    response = requests.get(f"{BASE_URL}/books/{BOOK2_ID}")
    assert response.status_code == 404

def test_post_wrong_genre():
    response = requests.post(f"{BASE_URL}/books", json=book5)
    assert response.status_code == 422