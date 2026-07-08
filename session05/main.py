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
@app.post("/products")
#ktr trùng tên spham
def create_product(product_request:ProductCeateRequest):
    for product in product:
        if product["product_name"] == product_request["product_name"]:
            return{"message":"Tên spham đã tồn tại"}
#Thêm phần tử vào List
    product.append(product_request)
    return{"message":"Thêm mới sản phẩm thành công","data":product_request}