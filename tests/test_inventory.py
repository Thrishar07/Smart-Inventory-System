
from unittest.mock import patch


def test_create_inventory_success(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchone.return_value = (
        101, 1, 50, 10, 5
    )

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.post(
            "/inventory/",
            json={
                "product_id": 1,
                "quantity_on_hand": 50,
                "reorder_level": 10,
                "safety_stock": 5
            }
        )

    assert response.status_code == 200
    assert response.json()["product_id"] == 1
    assert response.json()["quantity_on_hand"] == 50


def test_create_inventory_negative_stock(client):
    response = client.post(
        "/inventory/",
        json={
            "product_id": 1,
            "quantity_on_hand": -10,
            "reorder_level": 10,
            "safety_stock": 5
        }
    )

    assert response.status_code == 422


def test_create_inventory_duplicate(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.execute.side_effect = Exception(
        "Duplicate inventory record"
    )

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.post(
            "/inventory/",
            json={
                "product_id": 1,
                "quantity_on_hand": 50,
                "reorder_level": 10,
                "safety_stock": 5
            }
        )

    assert response.status_code == 400


def test_get_inventory_success(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchall.return_value = [
        (1, "Rice 5kg", "RICE-001", 100, 10, 5, None)
    ]

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.get("/inventory/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Rice 5kg"
    assert response.json()[0]["quantity_on_hand"] == 100


def test_update_inventory_success(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchone.return_value = (1, 75, 10, 5)

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.put(
            "/inventory/1",
            json={"quantity_on_hand": 75}
        )

    assert response.status_code == 200
    assert response.json()["quantity_on_hand"] == 75
    assert response.json()["message"] == "Inventory updated successfully"


def test_update_nonexistent_inventory(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.fetchone.return_value = None

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.put(
            "/inventory/999",
            json={"quantity_on_hand": 75}
        )

    assert response.status_code == 404


def test_update_inventory_database_failure(client, mock_db):
    cursor = mock_db["cursor"]

    cursor.execute.side_effect = Exception(
        "Database unavailable"
    )

    with patch(
        "app.api.inventory.get_connection",
        return_value=mock_db["connection"]
    ):
        response = client.put(
            "/inventory/1",
            json={"quantity_on_hand": 75}
        )

    assert response.status_code == 500
