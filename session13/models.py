#TẠO CÁC BẢNG DỮ LIỆU ÁNH XẠ ĐẾN MYSQL
from sqlalchemy import Column,Identity,String,Float
from sqlalchemy.orm import declarative_base
Base = declarative_base()
class Product(Base):
    __tablename__="product"
    id = Column(Identity)
    name = Column(String(50))