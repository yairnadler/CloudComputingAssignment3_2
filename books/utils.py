# utils.py
import json
from pymongo import MongoClient
import requests
from bson.objectid import ObjectId
import logging

GENRE = ['Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other']

# MongoDB client setup
try:
    client = MongoClient('mongodb://mongo:27017/')
    db = client.library
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {str(e)}")
    raise

def fetch_google_books_details(isbn):
    google_books_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    response = requests.get(google_books_url)
    if response.status_code == 200:
        items = response.json().get('items')
        if items:
            volume_info = items[0]['volumeInfo']
            authors = " and ".join(volume_info.get('authors', []))
            publisher = volume_info.get('publisher', 'missing')
            published_date = volume_info.get('publishedDate', 'missing')
            if len(published_date) == 4:
                published_date = f"{published_date}"
                
            return authors, publisher, published_date
        
    return None, None, None

def validate_book_data(data):
    required_fields = ['ISBN', 'title', 'genre']
    if all(field in data for field in required_fields):
        if data["genre"] not in GENRE:
            
            return False, f"Invalid Genre. Genre must be one of: {GENRE}"
        
        return True, None
    
    return False, "Missing required fields"

def validate_book_put_request_data(data):
    required_fields = ['ISBN', 'authors', 'genre', 'id', 'publishedDate', 'publisher', 'title']
    if all(field in data for field in required_fields):
        if data["genre"] not in GENRE:
            return False, f"Invalid Genre. Genre must be one of: {GENRE}"
        
        return True, None
    
    return False, "Missing required fields"

def create_book_entry(data):
    authors, publisher, published_date = fetch_google_books_details(data["ISBN"])

    if authors is None or publisher is None or published_date is None:
        raise Exception("Google")

    book_data = {
        "ISBN": data["ISBN"],
        "title": data["title"],
        "genre": data["genre"],
        "authors": authors if authors else 'missing',
        "publisher": publisher if publisher else 'missing',
        "publishedDate": published_date if published_date else 'missing',
        "id": str(ObjectId())
    }

    db_book_data = book_data.copy()
    db.books.insert_one(db_book_data)

    return book_data

def get_books(query_filter):
    books = list(db.books.find(query_filter, {'_id': False}))

    for book in books:
        if 'id' in book:
            book['id'] = str(book['id'])
            
    return books

def get_book_by_id(book_id):
    book = db.books.find_one({"id": book_id}, {'_id': False})
    
    if book:
        book['id'] = str(book['id'])
        
    return book

def delete_book_by_id(book_id):
    db.books.delete_one({"id": book_id})
    db.ratings.delete_one({"id": book_id})

def update_book_entry(book_id, data):
    db.books.update_one({"id": book_id}, {"$set": data})
    
    return get_book_by_id(book_id)

def create_rating_entry(book_id):
    rating_data = {
        "values": [],
        "average": 0.0,
        "title": db.books.find_one({"id": book_id})['title'],
        "id": book_id
    }
    
    db.ratings.insert_one(rating_data)

def get_ratings():
    ratings = list(db.ratings.find({}, {'_id': False}))
    for rating in ratings:
        rating['id'] = str(rating['id'])

    return ratings

def get_ratings_by_book_id(book_id):
    ratings = db.ratings.find_one({"id": book_id}, {'_id': False})
    
    if ratings:
        ratings['id'] = str(ratings['id'])
        
    return ratings

def add_rating(book_id, rating):
    rating_data = db.ratings.find_one({"id": book_id})
    
    if rating_data:
        rating_data["values"].append(rating)
        rating_data["average"] = sum(rating_data["values"]) / len(rating_data["values"])
        db.ratings.update_one({"id": book_id}, {"$set": rating_data})
        
        return rating_data["average"]
    
    return None

def get_top_books():
    db_top_books = db.ratings.find({"average": {"$gte": 3}}).sort("average", -1).limit(3)
    top_books_list = list(db_top_books)
    top_books = []
    
    for book in top_books_list:
        book_copy = {key: book[key] for key in book if key != '_id'}
        top_books.append(book_copy)
        
    return top_books
