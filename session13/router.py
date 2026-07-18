from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from services import get_all_product,get_product_detail,add_new_product

#TẠO CÁC API 
router = APIRouter(
    prefix = "/products",
    tags = ["/product"]
)
@router.get("")
def get_product(db:Session = Depends(get_db)):
    return{
        "message":"lấy danh sách sản phẩm thành công",
        "data"   : get_all_product(db)
    }

#VIẾT API LẤY CHI TIẾT SẢN PHẨM
@router.get("/{product}")
def get_product_by_id(product_id:int,db:Session=Depends(get_db)):
    return get_product_detail(product_id,db)
#VIẾT API THÊM SẢN PHẨM
@router.post("")
def add_product(product,db:Session=Depends(get_db)):
    return add_new_product
@router.put("")
def updata_product(product_id:int,db:Session=Depends(get_db)):
    return updata_product()
