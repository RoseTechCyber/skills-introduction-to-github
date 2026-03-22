# HealthyFoods API – POST and GET Documentation

Base URL: `http://localhost:5000/api`

All request and response bodies use **JSON** (`Content-Type: application/json`).

---

## Customers

### GET /api/customers
Returns a list of **all customers**, each including their full orders history.

**Response 200**
```json
[
  {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "555-1234",
    "address": "1 Main St",
    "created_at": "2024-01-15T10:30:00",
    "orders": [
      {
        "id": 1,
        "customer_id": 1,
        "caterer_id": 2,
        "items": "Grilled Salmon, Green Tea",
        "total_price": 22.50,
        "status": "delivered",
        "notes": null,
        "created_at": "2024-01-15T12:00:00",
        "updated_at": "2024-01-15T12:00:00"
      }
    ]
  }
]
```

---

### GET /api/customers/{id}
Returns a **single customer** by ID, including their full orders history.

| Parameter | Type    | Location | Description       |
|-----------|---------|----------|-------------------|
| `id`      | integer | path     | Customer ID       |

**Response 200**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "555-1234",
  "address": "1 Main St",
  "created_at": "2024-01-15T10:30:00",
  "orders": []
}
```

**Response 404** – Customer not found.

---

### POST /api/customers
Creates a **new customer**.

**Request body**

| Field     | Type   | Required | Description            |
|-----------|--------|----------|------------------------|
| `name`    | string | ✅       | Customer full name      |
| `email`   | string | ✅       | Unique e-mail address  |
| `phone`   | string | ❌       | Contact phone number   |
| `address` | string | ❌       | Delivery address        |

```json
{
  "name": "Bob Jones",
  "email": "bob@example.com",
  "phone": "555-5678",
  "address": "42 Oak Ave"
}
```

**Response 201** – Created customer object (with an empty `orders` list).

**Response 400** – Missing required field(s).

**Response 409** – A customer with the supplied e-mail already exists.

---

## Orders

### GET /api/orders
Returns a list of **all orders**, each including the associated customer and caterer summary.

**Response 200**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "caterer_id": 2,
    "items": "Grilled Salmon, Green Tea",
    "total_price": 22.50,
    "status": "delivered",
    "notes": "Extra lemon please",
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T12:00:00",
    "customer": { "id": 1, "name": "Alice Smith", "email": "alice@example.com" },
    "caterer":  { "id": 2, "name": "Best Bites Co", "specialty": "Vegan" }
  }
]
```

---

### GET /api/orders/{id}
Returns a **single order** by ID.

| Parameter | Type    | Location | Description  |
|-----------|---------|----------|--------------|
| `id`      | integer | path     | Order ID     |

**Response 200** – Order object (same shape as the list item above).

**Response 404** – Order not found.

---

### POST /api/orders
Creates a **new order** for a customer.  
> The new order is automatically linked to the customer's orders list in the database.  
> The response includes both the new order **and** the updated customer record so
> callers can confirm the customer's orders table has been updated.

**Request body**

| Field         | Type    | Required | Description                                            |
|---------------|---------|----------|--------------------------------------------------------|
| `customer_id` | integer | ✅       | ID of the customer placing the order                   |
| `items`       | string  | ✅       | Comma-separated list of menu items                     |
| `total_price` | number  | ✅       | Order total in USD                                     |
| `caterer_id`  | integer | ❌       | ID of the caterer fulfilling the order                 |
| `status`      | string  | ❌       | `pending` (default) · `confirmed` · `delivered` · `cancelled` |
| `notes`       | string  | ❌       | Special instructions                                   |

```json
{
  "customer_id": 1,
  "caterer_id": 2,
  "items": "Grilled Salmon, Green Tea",
  "total_price": 22.50,
  "status": "pending",
  "notes": "Extra lemon please"
}
```

**Response 201**
```json
{
  "order": {
    "id": 3,
    "customer_id": 1,
    "caterer_id": 2,
    "items": "Grilled Salmon, Green Tea",
    "total_price": 22.50,
    "status": "pending",
    "notes": "Extra lemon please",
    "created_at": "2024-01-16T09:00:00",
    "updated_at": "2024-01-16T09:00:00",
    "customer": { "id": 1, "name": "Alice Smith", "email": "alice@example.com" },
    "caterer":  { "id": 2, "name": "Best Bites Co", "specialty": "Vegan" }
  },
  "customer": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "orders": [
      { "id": 1, "items": "Caesar Salad", "total_price": 10.00, "status": "delivered" },
      { "id": 3, "items": "Grilled Salmon, Green Tea", "total_price": 22.50, "status": "pending" }
    ]
  }
}
```

**Response 400** – Missing required field(s) or invalid value.

**Response 404** – Customer or caterer not found.

---

## Caterers

### GET /api/caterers
Returns a list of **all caterers**.

**Response 200**
```json
[
  {
    "id": 1,
    "name": "Best Bites Co",
    "email": "bestbites@example.com",
    "phone": "555-9999",
    "specialty": "Vegan",
    "rating": 4.8,
    "created_at": "2024-01-01T08:00:00"
  }
]
```

---

### GET /api/caterers/{id}
Returns a **single caterer** by ID.

| Parameter | Type    | Location | Description   |
|-----------|---------|----------|---------------|
| `id`      | integer | path     | Caterer ID    |

**Response 200** – Caterer object (same shape as list item above).

**Response 404** – Caterer not found.

---

### POST /api/caterers
Adds a **new caterer** to the database.

**Request body**

| Field       | Type   | Required | Description                       |
|-------------|--------|----------|-----------------------------------|
| `name`      | string | ✅       | Caterer / company name            |
| `email`     | string | ✅       | Unique contact e-mail             |
| `phone`     | string | ❌       | Contact phone number              |
| `specialty` | string | ❌       | Type of cuisine / specialty       |
| `rating`    | number | ❌       | Rating out of 5.0                 |

```json
{
  "name": "Green Garden Catering",
  "email": "green@example.com",
  "phone": "555-3333",
  "specialty": "Mediterranean",
  "rating": 4.5
}
```

**Response 201** – Created caterer object.

**Response 400** – Missing required field(s) or invalid value.

**Response 409** – A caterer with the supplied e-mail already exists.

---

## Error Responses

All error responses follow a consistent shape:

```json
{ "error": "Human-readable description of the problem" }
```

| HTTP Status | Meaning                            |
|-------------|------------------------------------|
| 400         | Bad request / validation failure   |
| 404         | Resource not found                 |
| 409         | Conflict (duplicate unique field)  |
