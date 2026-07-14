#BÀI KIỂM TRA MINI PRODUCK
from fastapi import FastAPI
from pydantic import BaseModel,Field

tickets_db = [
    {"id": 1, "movie_name": "Doctor Strange 3", "room_code": "IMAX-01", "quantity": 2, "status": "confirmed"},
    {"id": 2, "movie_name": "Avatar 3", "room_code": "PREMIUM-02", "quantity": 1, "status": "confirmed"}
]

app = FastAPI()
class TicketCreate(BaseModel):
    movie_name : str
    room_sode : str
    quantity : str


@app.get("/")
def tickets():
    return {
        "message":"Lấy danh sách vé thành công",
        "data": tickets_db
    }

#LẤY DANH SÁCH VÉ
@app.post("/tickets")
def add_ticket(new_ticket: TicketCreate):
    print("new_ticket",new_ticket)
    add_new_ticket = {
  "statusCode": 201,
  "message": "Đặt vé thành công!",
  "data": {
    "id": 3,
    "movie_name": "Lật Mặt 9",
    "room_code": "STANDARD-03",
    "quantity": 3,
    "status": "confirmed",
  },
  "error": None,
    "path": "/tickets"
}

    tickets.append(add_new_ticket)
    return{
  "statusCode": 400,
  "message": "Lỗi: Vé xem phim tại phòng chiếu này đã được đặt!",
  "data": None,
  "error": "ERR-CINE-01: Ticket conflict for movie and room combination.",
  "path": "/tickets"
}


#XÓA VÉ
@app.delete("/tickets/ticket_id")
def delete_c(ticket_id:int):
    print("id vé cần xóa", ticket_id)
    for ticket in ticket_id:
        if ticket["id"] == ticket_id:
            return{
        "statusCode": 200,
        "message": "Hủy vé thành công!",
        "data": None,
        "error": None,
        "path": "/tickets/1"
}

    return{
        "statusCode": 404,
        "message": "Lỗi: Không tìm thấy mã vé yêu cầu!",
        "data": None,
        "error": "ERR-CINE-02: Ticket ID does not exist.",
        "path": "/tickets/99"
}
