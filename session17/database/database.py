from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autoflussh = False,
    autocommit = False,
    bind = engine
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()