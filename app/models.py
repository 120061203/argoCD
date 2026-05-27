from sqlalchemy import Column, Integer, String, Float
from pydantic import BaseModel
from typing import Optional

from database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)


class ItemCreate(BaseModel):
    name: str
    description: str = ""
    price: float


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float

    model_config = {"from_attributes": True}
