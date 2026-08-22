import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )
    return hashed_password.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# Dữ liệu kiểm thử
password = "Rikkei@123"

hashed_password = hash_password(password)

print("Hashed password:", hashed_password)
print("MK1:", verify_password("Rikkei@123", hashed_password))
print("MK2:", verify_password("Rikkei@456", hashed_password))

# Câu hỏi bổ sung
# 1. Vì sao không nên lưu mật khẩu trực tiếp vào database?
# Vì nếu database bị lộ, kẻ xấu có thể nhìn thấy mật khẩu thật của người dùng. Băm bằng Bcrypt giúp 
# không lưu mật khẩu ở dạng văn bản thuần túy.

# 2. Vì sao cùng một mật khẩu nhưng hai lần băm có thể tạo ra hai chuỗi hash khác nhau?
# Vì mỗi lần bcrypt.gensalt() tạo ra một Salt ngẫu nhiên khác nhau. Salt được kết hợp với mật khẩu trước khi băm 
# nên kết quả hash cũng khác nhau.

# 3. Salt có tác dụng gì trong việc chống Rainbow Table?
# Salt làm cho cùng một mật khẩu tạo ra các hash khác nhau, khiến các bảng hash được 
# tính toán sẵn (Rainbow Table) khó sử dụng để dò ngược mật khẩu.