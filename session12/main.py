from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services import get_all_product, get_product_detail

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "API đang hoạt động ổn định"
    }


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return get_all_product(db)

#API lấy dsach sản phẩm
@app.get("product/{product_id}")
def get_product_by_id(product_id:int,db:Session=Depends(get_db)):
    return get_product_detail(product_id,db)