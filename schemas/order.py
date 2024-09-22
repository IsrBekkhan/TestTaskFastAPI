from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
import schemas


class Order(BaseModel):
    product_id: int = Field(
        ...,
        description="Идентификатор (ID) товара",
        gt=0
    )
    quantity: int = Field(
        ...,
        description="Количество товара в заказе",
        gt=0
    )

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(Order):
    id: int


class OrderDetails(BaseModel):
    id: int
    quantity: int
    status: Optional[str]
    created_at: datetime
    product: schemas.Product

    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):
    status_id: int = Field(
        ...,
        description="Идентификатор (ID) статуса",
        ge=1,
        le=3,
    )
