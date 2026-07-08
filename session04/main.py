from fastapi import FastAPI
#Bộ API quản lí spham
@app.get("product")
def get_product():
    return "Lấy danh sách sản phẩm"
#Danh sách sản phẩm 
@app.get("products")
def get_product():
    return {
        "message":"Lấy danh sách sản phẩm thành công",
        "data":products
        }