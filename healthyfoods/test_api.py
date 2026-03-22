"""
Tests for the HealthyFoods REST API.

Run with:
    cd healthyfoods
    pip install -r requirements.txt pytest
    pytest test_api.py -v
"""
import pytest
from app import create_app
from models import db as _db


TEST_CONFIG = {
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}


@pytest.fixture
def app():
    application = create_app(test_config=TEST_CONFIG)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Reset database tables between tests."""
    with app.app_context():
        _db.create_all()
        yield
        _db.session.remove()
        _db.drop_all()


# ─────────────────────────────────────────────
# CUSTOMER TESTS
# ─────────────────────────────────────────────

def test_get_customers_empty(client):
    response = client.get("/api/customers")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_customer(client):
    payload = {"name": "Alice", "email": "alice@example.com", "phone": "555-1234", "address": "1 Main St"}
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["orders"] == []


def test_create_customer_missing_fields(client):
    response = client.post("/api/customers", json={"name": "Bob"})
    assert response.status_code == 400
    assert "email" in response.get_json()["error"]


def test_create_customer_duplicate_email(client):
    payload = {"name": "Alice", "email": "alice@example.com"}
    client.post("/api/customers", json=payload)
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]


def test_get_customer_by_id(client):
    client.post("/api/customers", json={"name": "Carol", "email": "carol@example.com"})
    response = client.get("/api/customers/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Carol"


def test_get_customer_not_found(client):
    response = client.get("/api/customers/999")
    assert response.status_code == 404


# ─────────────────────────────────────────────
# CATERER TESTS
# ─────────────────────────────────────────────

def test_get_caterers_empty(client):
    response = client.get("/api/caterers")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_caterer(client):
    payload = {"name": "Best Bites Co", "email": "bestbites@example.com", "specialty": "Vegan", "rating": 4.8}
    response = client.post("/api/caterers", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Best Bites Co"
    assert data["specialty"] == "Vegan"
    assert data["rating"] == 4.8


def test_create_caterer_missing_fields(client):
    response = client.post("/api/caterers", json={"name": "No Email"})
    assert response.status_code == 400


def test_create_caterer_duplicate_email(client):
    payload = {"name": "Best Bites Co", "email": "bestbites@example.com"}
    client.post("/api/caterers", json=payload)
    response = client.post("/api/caterers", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.get_json()["error"]


def test_get_caterer_by_id(client):
    client.post("/api/caterers", json={"name": "Fresh Feast", "email": "freshfeast@example.com"})
    response = client.get("/api/caterers/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Fresh Feast"


def test_get_caterer_not_found(client):
    response = client.get("/api/caterers/999")
    assert response.status_code == 404


# ─────────────────────────────────────────────
# ORDER TESTS
# ─────────────────────────────────────────────

def test_get_orders_empty(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_order_updates_customer(client):
    """Creating an order must appear in the customer's orders list."""
    client.post("/api/customers", json={"name": "Dave", "email": "dave@example.com"})

    order_payload = {
        "customer_id": 1,
        "items": "Salad, Juice",
        "total_price": 15.50,
    }
    response = client.post("/api/orders", json=order_payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["order"]["customer_id"] == 1
    assert data["order"]["total_price"] == 15.50
    assert data["order"]["status"] == "pending"

    # Customer's orders list must now contain the new order
    customer = data["customer"]
    assert len(customer["orders"]) == 1
    assert customer["orders"][0]["id"] == data["order"]["id"]


def test_create_order_with_caterer(client):
    client.post("/api/customers", json={"name": "Eve", "email": "eve@example.com"})
    client.post("/api/caterers", json={"name": "Green Garden", "email": "green@example.com", "specialty": "Salads"})

    order_payload = {
        "customer_id": 1,
        "caterer_id": 1,
        "items": "Caesar Salad, Water",
        "total_price": 12.00,
    }
    response = client.post("/api/orders", json=order_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["order"]["caterer_id"] == 1
    assert data["order"]["caterer"]["name"] == "Green Garden"


def test_create_order_invalid_customer(client):
    response = client.post("/api/orders", json={"customer_id": 999, "items": "Salad", "total_price": 10.0})
    assert response.status_code == 404
    assert "999" in response.get_json()["error"]


def test_create_order_invalid_caterer(client):
    client.post("/api/customers", json={"name": "Frank", "email": "frank@example.com"})
    response = client.post("/api/orders", json={
        "customer_id": 1,
        "caterer_id": 999,
        "items": "Wrap",
        "total_price": 8.0,
    })
    assert response.status_code == 404
    assert "999" in response.get_json()["error"]


def test_create_order_missing_fields(client):
    response = client.post("/api/orders", json={"customer_id": 1})
    assert response.status_code == 400


def test_create_order_invalid_status(client):
    client.post("/api/customers", json={"name": "Grace", "email": "grace@example.com"})
    response = client.post("/api/orders", json={
        "customer_id": 1,
        "items": "Smoothie",
        "total_price": 6.0,
        "status": "unknown",
    })
    assert response.status_code == 400


def test_get_order_by_id(client):
    client.post("/api/customers", json={"name": "Hank", "email": "hank@example.com"})
    client.post("/api/orders", json={"customer_id": 1, "items": "Soup", "total_price": 9.0})
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    assert response.get_json()["items"] == "Soup"


def test_get_order_not_found(client):
    response = client.get("/api/orders/999")
    assert response.status_code == 404


def test_multiple_orders_update_customer(client):
    """Multiple orders for the same customer are all visible on the customer record."""
    client.post("/api/customers", json={"name": "Ivy", "email": "ivy@example.com"})
    client.post("/api/orders", json={"customer_id": 1, "items": "Salad", "total_price": 7.0})
    client.post("/api/orders", json={"customer_id": 1, "items": "Wrap", "total_price": 9.0})

    response = client.get("/api/customers/1")
    assert response.status_code == 200
    customer = response.get_json()
    assert len(customer["orders"]) == 2
