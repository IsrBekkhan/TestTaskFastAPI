from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import delete, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import models
from database import Base
import schemas


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100), unique=True)
    description: Mapped[str] = mapped_column(String(length=500), server_default="")
    price: Mapped[float] = mapped_column(server_default="0")
    quantity: Mapped[int] = mapped_column(server_default="0")

    @classmethod
    async def add_product(
            cls,
            db_async_session: AsyncSession,
            product_schema: schemas.Product
    ) -> "models.Product":
        new_product = Product(**product_schema.dict())

        db_async_session.add(new_product)
        try:
            await db_async_session.commit()
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product '%s' already exists" % new_product.name
            )

        return new_product

    @classmethod
    async def get_products(
            cls, db_async_session: AsyncSession
    ) -> Sequence["models.Product"]:
        result = await db_async_session.execute(
            select(Product)
        )
        products = result.unique().scalars().all()
        await db_async_session.aclose()

        return products

    @classmethod
    async def get_product(
            cls,
            db_async_session: AsyncSession,
            product_id: int,
    ) -> "models.Product":
        result = await db_async_session.execute(
            select(Product).where(Product.id == product_id)
        )
        await db_async_session.aclose()
        product = result.unique().scalars().one_or_none()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product with ID '%s' does not exist" % product_id
            )

        return product

    @classmethod
    async def update_product(
            cls,
            db_async_session: AsyncSession,
            product_id: int,
            product_schema: schemas.Product,
    ) -> "models.Product":
        product = await cls.get_product(db_async_session, product_id)
        product.name, product.description = product_schema.name, product_schema.description
        product.price, product.quantity = product_schema.price, product_schema.quantity
        try:
            async with db_async_session.begin():
                await db_async_session.merge(product)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product '%s' already exists" % product.name
            )

        return product

    @classmethod
    async def delete_product(
            cls,
            db_async_session: AsyncSession,
            product_id: int,
    ) -> None:
        await db_async_session.execute(
            delete(Product).where(Product.id == product_id)
        )
        await db_async_session.commit()

