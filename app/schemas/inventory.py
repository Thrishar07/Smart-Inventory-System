from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity_on_hand: int = Field(ge=0)
    reorder_level: int = Field(ge=0)
    safety_stock: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    quantity_on_hand: int = Field(ge=0)
    