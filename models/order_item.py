from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
import models


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", onupdate="CASCADE", ondelete="CASCADE"),
        default=None,
        nullable=True,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", onupdate="CASCADE", ondelete="CASCADE"),
        default=None,
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(server_default="0")

    product: Mapped[models.Product] = relationship(lazy='joined')
    order: Mapped[models.Order] = relationship(lazy='joined')
