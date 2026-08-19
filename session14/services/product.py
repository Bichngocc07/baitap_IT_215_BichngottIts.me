"""
VIẾT CÁC HÀM LẤY DỮ LIỆU TRONG DB
"""

from app.models.product import Product

# hàm lấy danh sách sản phẩm


def get_products(db):
    products = db.query(Product).all()
    return {
        "message": "Lấy danh sách sản phẩm",
        "data": products
    }