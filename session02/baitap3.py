from fastapi import FastAPI

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Python Basic",
        "author": "Lê Minh Thu",
        "category": "programming",
        "year": 2022,
        "is_available": True
    },
    {
        "id": 2,
        "title": "HTML CSS",
        "author": "Nguyễn Văn B",
        "category": "web",
        "year": 2020,
        "is_available": False
    },
    {
        "id": 3,
        "title": "JavaScript",
        "author": "Trần Văn C",
        "category": "web",
        "year": 2021,
        "is_available": True
    },
    {
        "id": 4,
        "title": "MySQL",
        "author": "Lê Văn D",
        "category": "database",
        "year": 2019,
        "is_available": True
    },
    {
        "id": 5,
        "title": "Computer Network",
        "author": "Nguyễn Văn E",
        "category": "network",
        "year": 2021,
        "is_available": False
    },
    {
        "id": 6,
        "title": "FastAPI Basic",
        "author": "Nguyễn Văn A",
        "category": "web",
        "year": 2023,
        "is_available": True
    }
]

@app.get("/books/statistics")
def get_statistics():
    total_books = len(books)
    available_books = len(
        [book for book in books if book["is_available"]]
    )
    borrowed_books = len(
        [book for book in books if not book["is_available"]]
    )
    return {
            "total_books": total_books,
            "available_books": available_books,
            "borrowed_books": borrowed_books
    }

@app.get("/books/categories")
def get_categories():
    categories = list(
        set(book["category"] for book in books)
    )
    return {
        "categories" :categories
    }

@app.get("/books/latest")
def get_latest():
    if not books :
        return {
                "message": "No books available"
                }
    latest_book = books[0]
    for book in books:
        if book["year"] > latest_book["year"]:
            latest_book = book
    return latest_book