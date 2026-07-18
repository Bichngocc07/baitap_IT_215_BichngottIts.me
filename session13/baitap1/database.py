from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Thay đổi tài khoản/mật khẩu MySQL phù hợp với máy của bạn
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency cấp phiên làm việc và thu hồi kết nối tự động
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()