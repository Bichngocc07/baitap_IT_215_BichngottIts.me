from sqlalchemy.orm import Session
from models import MenuItem
from schemas import MenuItemSchema

# 1. Lấy danh sách toàn bộ món ăn
def get_all_items(db: Session):
    return db.query(MenuItem).all()

# 2. Lấy thông tin chi tiết một món ăn
def get_item_by_id(item_id: int, db: Session):
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()

# 3. Thêm mới món ăn món ăn (Bẫy trùng mã món ăn dish_code)
def create_menu_item(item_in: MenuItemSchema, db: Session):
    # Kiểm tra trùng lặp mã món ăn
    exists = db.query(MenuItem).filter(MenuItem.dish_code == item_in.dish_code).first()
    if exists:
        return "DUPLICATE_CODE"

    try:
        new_item = MenuItem(**item_in.model_dump())
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as e:
        db.rollback()
        raise e

# 4. Cập nhật thông tin món ăn (PUT)
def update_menu_item(item_id: int, item_in: MenuItemSchema, db: Session):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        return None  # Không tìm thấy

    try:
        # Sử dụng exclude_unset=True lọc dữ liệu và setattr ghi đè động thuộc tính
        update_data = item_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise e

# 5. Xóa món ăn khỏi hệ thống (DELETE)
def delete_menu_item(item_id: int, db: Session):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not db_item:
        return None  # Không tìm thấy

    try:
        db.delete(db_item)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e