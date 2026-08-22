import jwt
from datetime import datetime, timedelta, timezone


SECRET_KEY = "my-secret-key-123"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    payload["exp"] = expire

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise Exception("Token đã hết hạn")

    except jwt.InvalidTokenError:
        raise Exception("Token không hợp lệ")


# Dữ liệu kiểm thử
token = create_access_token(
    data={
        "sub": "student01@gmail.com",
        "user_id": 1,
        "role": "student"
    },
    expires_minutes=30
)

print("Access Token:")
print(token)

print("\nDecoded Token:")
print(decode_access_token(token))

# 4. Giải thích câu hỏi bổ sung
# 1. Ba phần của JWT là gì?
# JWT gồm 3 phần:
# Header.Payload.Signature
# Header: chứa thông tin thuật toán, ví dụ HS256.
# Payload: chứa dữ liệu như sub, user_id, role, exp.
# Signature: chữ ký dùng để kiểm tra token có bị thay đổi hay không.

# 2. Payload có được mã hóa để che giấu dữ liệu không?
# Không.
# Payload của JWT thường chỉ được Base64URL encode, không phải mã hóa bảo 
# mật. Người khác có thể giải mã Payload và đọc được dữ liệu.
# Vì vậy không được đưa mật khẩu hoặc password_hash vào Payload.

# 3. Signature có vai trò gì?
# Signature giúp server kiểm tra:
# Token có đúng do server ký và có bị thay đổi sau khi tạo hay không.
# Server dùng SECRET_KEY để kiểm tra chữ ký.