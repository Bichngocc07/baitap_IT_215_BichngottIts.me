from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Nhớ thay đổi "password" theo đúng cấu hình MySQL của bạn
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/connect_db"

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency quản lý phiên làm việc, tự thu hồi kết nối tránh rò rỉ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # KHẮC PHỤC TRIỆT ĐỂ: Giải phóng kết nối vật lý