from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    total = Column(Float)
    status = Column(String)

class ProductOut(BaseModel):
    id: int
    order_id: int
    total: float
    status: str
    class Config:
        orm_mode = True