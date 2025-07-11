from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Product
from typing import List

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductIn(BaseModel):
    name: str
    stock: int

class ProductOut(BaseModel):
    id: int
    name: str
    stock: int
    class Config:
        orm_mode = True

@app.post("/products")
def create_product(product: ProductIn, db: Session = Depends(get_db)):
    new_product = Product(name=product.name, stock=product.stock)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created", "product_id": new_product.id}

@app.get("/products", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/products/{product_name}")
def get_product(product_name: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(name=product_name).first()
    if product:
        return {"name": product.name, "stock": product.stock}
    return {"error": "Product not found"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "inventory"}
