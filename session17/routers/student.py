from fastapi import APIRouter
router_student = APIRouter 
@router_student.get("/{student_id}")
def get_detail_student(student_id, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="sinh viên không tồn tại"
        )

    classroom = db.query(ClassRoom).filter(
        ClassRoom.id == student.class_id
    ).first()

    student.class_name = classroom.class_name

    return {
        "message": "lấy chi tiết sinh viên thành công!",
        "data": student,
    }


# API thêm sinh viên
@router_student.post("/")
def add_student(request: CreateStudent, db: Session = Depends(get_db)):
    # kiểm tra xem class_id có tồn tại hay không?
    classroom = db.query(ClassRoom).filter(
        ClassRoom.id == request.class_id
    ).first()