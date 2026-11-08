from pydantic import BaseModel, Field
from decimal import Decimal


class SaleCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SaleResponse(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    unit_price_at_sale: Decimal