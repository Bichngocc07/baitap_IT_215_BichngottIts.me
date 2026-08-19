"""
B1 TEST API 
B2 TẠO FOLDER
B3 TEST API THAO TÁC DỮ LIỆU
"""
from fastapi import FastAPI
app = FastAPI()
app.get("/")
def home():
    return{
        "message":"API đang chạy"
    }
    