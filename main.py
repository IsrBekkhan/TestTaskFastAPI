from contextlib import asynccontextmanager
from typing import Annotated, List, Sequence, Optional

from fastapi import Depends, FastAPI, status, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal, Base, engine
import models
import schemas


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db_async_session: AsyncSession = AsyncSessionLocal()
    await models.Status.create_statuses(db_async_session)
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Warehouse",
    summary="Документация API",
    description="""
    Сервис для управления процессами на складе.
    API позволяeт управлять товарами, складскими запасами и заказами.
    """,
    version="0.0.1",
    contact={
        "name": "Бекхан Исрапилов",
        "email": "israpal@bk.ru",
    },
)


# Database dependency
async def get_db_async_session():
    db_async_session: AsyncSession = AsyncSessionLocal()
    try:
        yield db_async_session
    finally:
        await db_async_session.aclose()


@app.post(
    "/api/products",
    summary="добавить новый товар",
    response_description="Успешное добавление нового товара",
    status_code=status.HTTP_201_CREATED,
    tags=["Товары"],
)
async def add_product(
    product: schemas.Product,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.ProductResponse:
    """
    Добавление нового товара в БД

    """
    return await models.Product.add_product(db_async_session, product)


@app.get(
    "/api/products",
    summary="получить все товары",
    response_description="Успешное получение всех товаров",
    status_code=status.HTTP_200_OK,
    tags=["Товары"],
)
async def get_products(
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> Sequence[schemas.ProductResponse]:
    """
    Возвращает список всех товаров

    """
    return await models.Product.get_products(db_async_session)


@app.get(
    "/api/products/{product_id}",
    summary="информация о товаре",
    response_description="Успешное получение информации о товаре",
    status_code=status.HTTP_200_OK,
    tags=["Товары"],
)
async def get_product(
    product_id: int,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.ProductResponse:
    """
    Возвращает информацию о товаре по ID

    """
    return await models.Product.get_product(db_async_session, product_id)


@app.put(
    "/api/products/{product_id}",
    summary="обновление информации о товаре",
    response_description="Успешное обновление информации о товаре",
    status_code=status.HTTP_200_OK,
    tags=["Товары"],
)
async def update_product(
    product_id: int,
    product: schemas.Product,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> Optional[schemas.ProductResponse]:
    """
    Обновляет информацию о товаре по ID

    """
    return await models.Product.update_product(db_async_session, product_id, product)


@app.delete(
    "/api/products/{product_id}",
    summary="удаление товара",
    response_description="Успешное удаление товара из БД",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Товары"],
)
async def delete_tweet(
    product_id: int,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> None:
    """
    Удаляет товар из БД по ID

    """
    return await models.Product.delete_product(db_async_session, product_id)


@app.post(
    "/api/orders",
    summary="добавить новый заказ",
    response_description="Успешное добавление нового заказа",
    status_code=status.HTTP_201_CREATED,
    tags=["Заказы"],
)
async def add_order(
    order: schemas.Order,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.OrderResponse:
    """
    Добавление нового заказа в БД.
    В теле запроса необходимо указать ID товара и его количество.

    """
    return await models.Order.add_order(db_async_session, order)


@app.get(
    "/api/orders",
    summary="получить все заказы",
    response_description="Успешное получение всех заказов",
    status_code=status.HTTP_200_OK,
    tags=["Заказы"],
)
async def get_orders(
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> Sequence[schemas.OrderResponse]:
    """
    Возвращает список всех заказов

    """
    return await models.Order.get_orders(db_async_session)


@app.get(
    "/api/orders/{order_id}",
    summary="информация о заказе",
    response_description="Успешное получение информации о заказе",
    status_code=status.HTTP_200_OK,
    tags=["Заказы"],
)
async def get_order(
    order_id: int,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.OrderDetails:
    """
    Возвращает информацию о заказе по ID

    """
    order_item = await models.Order.get_order(db_async_session, order_id)
    return schemas.OrderDetails(
            id=order_item.id,
            quantity=order_item.quantity,
            status=order_item.order.status.description,
            created_at=order_item.order.created_at,
            product=order_item.product
        )


@app.patch(
    "/api/orders/{order_id}",
    summary="обновление статуса",
    response_description="Успешное обновление статуса заказа",
    status_code=status.HTTP_200_OK,
    tags=["Заказы"],
)
async def update_status(
    order_id: int,
    status_schema: schemas.StatusUpdate,
    db_async_session: AsyncSession = Depends(get_db_async_session),
) -> schemas.OrderDetails:
    """
    Обновляет статус заказа.
    В теле запроса необходимо указать ID статуса, где
        1 - в процессе,
        2 - отправлен,
        3 - доставлен.
    """
    order_item = await models.Order.update_status(
        db_async_session, order_id, status_schema
    )
    return schemas.OrderDetails(
        id=order_item.id,
        quantity=order_item.quantity,
        status=order_item.order.status.description,
        created_at=order_item.order.created_at,
        product=order_item.product
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Обработчик исключений HTTPException

    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def uvicorn_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик непредвиденных исключений

    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=str(exc),
    )
