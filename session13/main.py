from fastapi import FastAPI
from router import router

app = FastAPI()
app.cl
@app.get("/")
def home():
    return{
        "message": "API đang chạy"
    }
#API LẤY TẤT CẢ SẢN PHẨM 
