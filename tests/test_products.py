
from unittest.mock import patch


def test_create_product_success(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchone.return_value = (
        101,
        "TEST-001",
        "Test Rice",
        "Groceries",
        120.00,
        1
    )

    with patch(
        "app.api.products.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.post(
            "/products/",
            json={
                "sku": "TEST-001",
                "name": "Test Rice",
                "category": "Groceries",
                "unit_price": 120.00,
                "supplier_id": 1
            }
        )

    assert response.status_code == 201
    assert response.json()["product_id"] == 101
    assert response.json()["name"] == "Test Rice"
    assert response.json()["supplier_id"] == 1


def test_create_product_invalid_price(client):
    response = client.post(
        "/products/",
        json={
            "sku": "TEST-002",
            "name": "Invalid Product",
            "category": "Groceries",
            "unit_price": -10,
            "supplier_id": 1
        }
    )

    assert response.status_code == 422


def test_create_product_duplicate_sku(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.execute.side_effect = Exception(
        "duplicate key value violates unique constraint"
    )

    with patch(
        "app.api.products.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.post(
            "/products/",
            json={
                "sku": "TEST-001",
                "name": "Duplicate Rice",
                "category": "Groceries",
                "unit_price": 120.00,
                "supplier_id": 1
            }
        )

    assert response.status_code == 400


def test_get_products_success(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchall.return_value = [
        (101, "TEST-001", "Test Rice", "Groceries", 120.00, 1)
    ]

    with patch(
        "app.api.products.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.get("/products/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Rice"
    assert response.json()[0]["supplier_id"] == 1


def test_get_products_database_failure(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.execute.side_effect = Exception("Database unavailable")

    with patch(
        "app.api.products.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.get("/products/")

    assert response.status_code == 500
