from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ĐỊA CHỈ CỦA DATABASE
DATABASE_URL = "mysql+pymysql://HuuDai:123456@localhost:3306/products"

# engine : cánh cửa để mở ra truy cập vào db
engine = create_engine(DATABASE_URL)

# TẠO PHIÊN LÀM VIỆC MỖI LẦN TƯƠNG TÁC VỚI DB
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

# VIẾT HÀM ĐỂ LÀM VIỆC VỚI DB


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()