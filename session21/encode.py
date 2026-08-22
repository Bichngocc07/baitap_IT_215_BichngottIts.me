# """
# MÃ HÓA MẬT KHẨU:
# 1.TẠI SAO CẦN MÃ HÓA :bảo vệ toàn vẹn dữ liệu
# 2.KHI NÀO CẦN TIẾN HÀNH MÃ HÓA :khi đăng kí tài khoản
# 3.MÃ HÓA NHƯ THẾ NÀO :
# Khi đăng kí tài khoản : Hệ thống sẽ dùng các kĩ thuật (bcrypt) để mã hóa (hash) mật khẩu để lưu vào databasse:
# 123456 -> abcxyz
# 12345 -> klmpq
# abcxyz : gồm 4 phần
#     1: Tên kỹ thuật mã hóa
#     2: Cost (Chi phí mã hóa)
#     3: Muối (Salt)
#     4: Hast (Chuỗi mật khẩu được mã hóa)
# Khi đăng nhập tài khoản:
#     B1: Nhập tên tài khoản + mật khẩu
#     B2: Hệ thống kiểm tra tài khoản có đúng hay không
#         +Nếu sai hiển thị thông báo : Tên tk hoặc mk không đúng
#         +Nếu đúng lấy ra mk được mã hóa
#     B3: Từ chuỗi mật khẩu đã được mã hóa lấy ra muối (salt) + pass mk sau đó verify mật khẩu
# MÃ HÓA 1 CHIỀU
# CÁC HACKER MUỐN HACK MẬT KHẨU ĐẦU TIÊN PHẢI CÓ ĐƯỢC CHUỖI MÃ HÓA TRONG DB SAU ĐÓ TẠO RA CÁC MK NGƯỜI DÙNG 
# VD : 123456. abc123@..
# KẾT HỢP SALT + ĐỂ VERIFY VỚI CHUỖI MÃ HÓA
# """

import bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )
    return hashed_password.decode("utf-8")
print("mk1", hash_password("ngocancut"))
print("mk2", hash_password("123456"))
print("mk3", hash_password("abcdef"))
# mk1 $2b$12$EdiDs4dfZoJS6ek7o4zUE.pMSXGV7w/EIsX8AYDmDw9iKuEgoeUEq
# mk2 $2b$12$JrYB/09P/HHO7YCISZkR0.1HHrWXk7QNMbq4CGSMujdghmOQhucWq
# mk3 $2b$12$P/BA1TekHns0BCDzh2Z4M.gV0.yF1KxToJgBxI58Z.t5Zi5QIAYOi
"""
    1.Tên kĩ thuật : $2b
    2.Chi phí      : $12
    3.Muối(Salt)   : $EdiDs4dfZoJS6ek7o4zUE
    4.mk sau khi mã hóa  EIsX8AYDmDw9iKuEgoeUEq
"""
#ĐĂNG NHẬP
def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-g"),
        hashed_password.encode("utf-g")
    )
print(verify_password("123456"))