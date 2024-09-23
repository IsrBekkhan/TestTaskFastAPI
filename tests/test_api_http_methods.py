import pytest

import models
import schemas


@pytest.mark.usefixtures("client", "db_session")
class TestProductRoutes:

    def test_successfully_response_when_get_products(self, client):
        response = client.get("/api/products")

        assert len(response.json()) == 3
        assert response.status_code == 200

    def test_successfully_response_when_get_product(self, client):
        response = client.get("/api/products/1")
        assert len(response.json()) == 5
        assert response.status_code == 200

    async def test_successfully_response_when_post_product(self, client, db_session):
        test_product = {
                "name": "Test product",
                "description": "Test description",
                "price": 50,
                "quantity": 50
            }
        response = client.post(
            "/api/products",
            json=test_product,
        )
        async_db_session = db_session()
        await models.Product.delete_product(async_db_session, product_id=response.json()["id"])
        assert len(response.json()) == 5
        assert response.status_code == 201

    def test_successfully_response_when_put_product(self, client):
        description = "Test description"
        response = client.put(
            "/api/products/1",
            json={
                "name": "Laptop",
                "description": description,
                "price": 1200.99,
                "quantity": 100
            }
        )
        assert len(response.json()) == 5
        assert response.json()["description"] == description
        assert response.status_code == 200

    async def test_successfully_response_when_delete_product(self, client, db_session):
        async_db_session = db_session()
        test_product = {
            "name": "Test product",
            "description": "Test description",
            "price": 50,
            "quantity": 50
        }
        product = await models.Product.add_product(async_db_session, schemas.Product(**test_product))
        products_before = await models.Product.get_products(async_db_session)

        response = client.delete(f"/api/products/{product.id}")

        products_after = await models.Product.get_products(async_db_session)
        assert len(products_before) == len(products_after) + 1
        assert response.status_code == 204

