from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload

from database import Base
import models
import schemas


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    status_id: Mapped[int] = mapped_column(
        ForeignKey("statuses.id", onupdate="CASCADE", ondelete="SET NULL"),
        default=1,
        nullable=True,
    )

    status: Mapped[models.Status] = relationship(lazy='joined')

    @classmethod
    async def add_order(
            cls,
            db_async_session: AsyncSession,
            order_schema: schemas.Order
    ) -> "models.OrderItem":
        product = await models.Product.get_product(db_async_session, order_schema.product_id)

        if product.quantity < order_schema.quantity:
            error_message = "Количество товара {product!r} на складе "\
                            "меньше запрашиваемого {quantity} шт."
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message.format(
                    product=product.name, quantity=order_schema.quantity
                )
            )
        async with db_async_session.begin():
            new_order_item = models.OrderItem(
                product=product,
                order=Order(),
                quantity=order_schema.quantity
            )
            db_async_session.add(new_order_item)
            product.quantity -= order_schema.quantity

        return new_order_item

    @classmethod
    async def get_orders(
            cls, db_async_session: AsyncSession
    ) -> Sequence["models.Order"]:
        result = await db_async_session.execute(
            select(models.OrderItem)
        )
        await db_async_session.aclose()
        return result.unique().scalars().all()

    @classmethod
    async def get_order(
            cls,
            db_async_session: AsyncSession,
            order_id: int
    ) -> "models.Order":
        result = await db_async_session.execute(
            select(models.OrderItem).where(models.OrderItem.id == order_id)
        )
        await db_async_session.aclose()
        order_item = result.unique().scalars().one_or_none()

        if order_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order with ID '%s' does not exist" % order_id
            )

        return order_item

    @classmethod
    async def update_status(
            cls,
            db_async_session: AsyncSession,
            order_id: int,
            status_schema: schemas.StatusUpdate,
    ) -> "models.Order":
        order_item = await cls.get_order(db_async_session, order_id)
        order_item.order.status_id = status_schema.status_id

        async with db_async_session.begin():
            await db_async_session.merge(order_item)

        return await cls.get_order(db_async_session, order_id)

