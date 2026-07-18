import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import MenuItemSchema, MenuItemResponse
import menu_service

# Tự động khởi tạo bảng vật lý trong MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Catering Menu Management System")

# Helper: Khởi tạo cấu trúc Response Envelope chuẩn hóa 6 trường bắt buộc
def make_unified_response(status_code: int, message: str, data=None, error=None, path: str = ""):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# API 1: Thêm món ăn mới (POST)
@app.post("/menu-items", status_code=status.HTTP_201_CREATED)
def api_create_item(request: Request, item_in: MenuItemSchema, db: Session = Depends(get_db)):
    result = menu_service.create_menu_item(item_in, db)
    
    if result == "DUPLICATE_CODE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=make_unified_response(400, "Mã món ăn đã tồn tại trên hệ thống", error="Bad Request", path=request.url.path)
        )
        
    response_data = MenuItemResponse.model_validate(result).model_dump()
    return make_unified_response(201, "Thêm món ăn thành công", data=response_data, path=request.url.path)


# API 2: Lấy danh sách toàn bộ món ăn (GET)
@app.get("/menu-items")
def api_get_all_items(request: Request, db: Session = Depends(get_db)):
    items = menu_service.get_all_items(db)
    response_data = [MenuItemResponse.model_validate(i).model_dump() for i in items]
    return make_unified_response(200, "Lấy danh sách món ăn thành công", data=response_data, path=request.url.path)


# API 3: Lấy thông tin chi tiết một món ăn (GET)
@app.get("/menu-items/{item_id}")
def api_get_item_detail(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = menu_service.get_item_by_id(item_id, db)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=make_unified_response(404, "Menu item not found", error="Not Found", path=request.url.path)
        )
        
    response_data = MenuItemResponse.model_validate(item).model_dump()
    return make_unified_response(200, "Lấy thông tin chi tiết món ăn thành công", data=response_data, path=request.url.path)


# API 4: Cập nhật thông tin món ăn (PUT)
@app.put("/menu-items/{item_id}")
def api_update_item(item_id: int, request: Request, item_in: MenuItemSchema, db: Session = Depends(get_db)):
    updated_item = menu_service.update_menu_item(item_id, item_in, db)
    
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=make_unified_response(404, "Menu item not found", error="Not Found", path=request.url.path)
        )
        
    response_data = MenuItemResponse.model_validate(updated_item).model_dump()
    return make_unified_response(200, "Cập nhật món ăn thành công", data=response_data, path=request.url.path)


# API 5: Xóa món ăn khỏi hệ thống (DELETE)
@app.delete("/menu-items/{item_id}")
def api_delete_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    deleted = menu_service.delete_menu_item(item_id, db)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=make_unified_response(404, "Menu item not found", error="Not Found", path=request.url.path)
        )
        
    return make_unified_response(200, "Xóa món ăn thành công", data=None, path=request.url.path)