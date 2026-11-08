from pydantic import BaseModel, Field
from decimal import Decimal


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    category: str | None = None
    unit_price: Decimal = Field(ge=0)
    supplier_id: int | None = None


class ProductResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    category: str | None
    unit_price: Decimal
    supplier_id: int | None