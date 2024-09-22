from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    name: str = Field(
        ...,
        description="Название товара",
        max_length=100,
        min_length=1
    )
    description: str = Field(
        ...,
        description="Описание товара",
        max_length=500,
        min_length=0
    )
    price: float = Field(
        ...,
        description="Цена товара",
        ge=0,
    )
    quantity: int = Field(
        ...,
        description="Количество товара на складе",
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(Product):
    id: int
