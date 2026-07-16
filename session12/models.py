from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float
Base = declarative_base()
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)