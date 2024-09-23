import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

from database import Base
from main import app, get_db_async_session
import models
import schemas

postgres = PostgresContainer(image="postgres:16.2", driver="asyncpg")
postgres.start()

engine = create_async_engine(postgres.get_connection_url(), poolclass=NullPool)
AsyncTestSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
async def db_session():
    yield AsyncTestSession
    postgres.stop()


@pytest.fixture(scope="session")
async def client(db_session):
    async def override_get_db():
        db: AsyncSession = db_session()
        try:
            yield db
        finally:
            await db.aclose()

    app.dependency_overrides[get_db_async_session] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def create_data(db_session: AsyncSession):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_db_session = db_session()

    await models.Status.create_statuses(async_db_session)

    await models.Product.add_product(
        async_db_session,
        schemas.Product(name="Laptop", description="Best laptop in market", price=1200.99, quantity=100)
    )
    await models.Product.add_product(
        async_db_session,
        schemas.Product(name="Phone", description="Best phone in market", price=600.99, quantity=200)
    )
    await models.Product.add_product(
        async_db_session,
        schemas.Product(name="Printer", description="Best printer in market", price=300.99, quantity=500)
    )
    await models.Order.add_order(
        async_db_session,
        schemas.Order(product_id=1, quantity=5)
    )
    await models.Order.add_order(
        async_db_session,
        schemas.Order(product_id=2, quantity=10)
    )
