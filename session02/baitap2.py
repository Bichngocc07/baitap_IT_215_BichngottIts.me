from fastapi import FastAPI 
app = FastAPI()
books = [
  {
    "id": 1,
    "title": "Python Basic",
    "author": "Nguyen Van A",
    "category": "programming",
    "year": 2022,
    "is_available" :True
  },
  {
    "id": 2,
    "title": "Web API Design",
    "author": "Tran Van B",
    "category": "web",
    "year": 2021,
    "is_available": False
  }
]

@app.get("/books") 
def get_books() :
    return books
@app.get("/books/available") 
def get_books_available() :
    rusle = []
    for i in books :
        if i['is_available'] == True :
            rusle.append(i)
    return i
@app.get("/books/borrowed") 
def get_books_borrowed() :
    rusles = []
    for i in books :
        if i['is_available'] == False :
            rusles.append(i)
    return i