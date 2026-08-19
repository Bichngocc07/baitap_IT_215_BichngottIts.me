from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.models.classrooms import ClassRoom

router_classroom = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"]
)

@router_classroom.get("")
def get_all_classrooms(db: Session = Depends(get_db)):
    classrooms = db.query(ClassRoom).all()

    return {
        "message": "Lấy danh sách tất cả lớp học!",
        "data": classrooms
    }