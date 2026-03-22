# HealthyFoods

A REST API for managing healthy food orders, customers, and caterers.

## Stack

- **Python 3.10+** / **Flask 3**
- **Flask-SQLAlchemy** (SQLite by default, swap via `DATABASE_URL`)

## Database Layout

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│  customers  │       │    orders    │       │   caterers   │
├─────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)     │◄──1:N─│ customer_id  │N:1───►│ id (PK)      │
│ name        │       │ caterer_id   │       │ name         │
│ email       │       │ items        │       │ email        │
│ phone       │       │ total_price  │       │ phone        │
│ address     │       │ status       │       │ specialty    │
│ created_at  │       │ notes        │       │ rating       │
└─────────────┘       │ created_at   │       │ created_at   │
                      │ updated_at   │       └──────────────┘
                      └──────────────┘
```

- A **Customer** can have many **Orders** (one-to-many).
- An **Order** belongs to one **Customer** and optionally one **Caterer**.
- A **Caterer** can fulfill many **Orders**.

## Quick Start

```bash
cd healthyfoods
pip install -r requirements.txt
python app.py
```

The server starts at `http://localhost:5000`.  
All endpoints are prefixed with `/api`.

## Running Tests

```bash
cd healthyfoods
pip install -r requirements.txt pytest
pytest test_api.py -v
```

## API Overview

See [`docs/POST_AND_GET_DOC.md`](docs/POST_AND_GET_DOC.md) for full documentation.

| Method | Endpoint             | Description                                     |
|--------|----------------------|-------------------------------------------------|
| GET    | /api/customers       | List all customers (with orders)                |
| POST   | /api/customers       | Create a customer                               |
| GET    | /api/customers/{id}  | Get a customer (with orders) by ID              |
| GET    | /api/orders          | List all orders                                 |
| POST   | /api/orders          | Create an order → updates customer orders table |
| GET    | /api/orders/{id}     | Get an order by ID                              |
| GET    | /api/caterers        | List all caterers                               |
| POST   | /api/caterers        | Add a caterer to the database                   |
| GET    | /api/caterers/{id}   | Get a caterer by ID                             |

### Key Behaviour

- **`POST /api/orders`** saves the order to the `orders` table *and* links it to
  the customer via the `customer_id` foreign key.  When you subsequently call
  `GET /api/customers/{id}`, the new order appears in the customer's `orders`
  list — demonstrating that the customer's orders table is always up to date.

- **`POST /api/caterers`** adds the caterer to the `caterers` table and the new
  record is immediately available via `GET /api/caterers`.
