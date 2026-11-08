
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_db():
    # Mock PostgreSQL connection
    connection = MagicMock()
    cursor = MagicMock()

    # Simulate database context managers
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False

    connection.cursor.return_value = cursor
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = False

    return {
        "connection": connection,
        "cursor": cursor
    }
