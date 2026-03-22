from flask import Blueprint, jsonify, request
from models import db, Customer, Order, Caterer

api = Blueprint("api", __name__)


# ─────────────────────────────────────────────
# CUSTOMER ROUTES
# ─────────────────────────────────────────────

@api.route("/customers", methods=["GET"])
def get_customers():
    """Return all customers with their associated orders."""
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers]), 200


@api.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Return a single customer (with orders) by ID."""
    customer = db.get_or_404(Customer, customer_id)
    return jsonify(customer.to_dict()), 200


@api.route("/customers", methods=["POST"])
def create_customer():
    """Create a new customer."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["name", "email"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if Customer.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "A customer with this email already exists"}), 409

    customer = Customer(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        address=data.get("address"),
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201


# ─────────────────────────────────────────────
# ORDER ROUTES
# ─────────────────────────────────────────────

@api.route("/orders", methods=["GET"])
def get_orders():
    """Return all orders."""
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders]), 200


@api.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """Return a single order by ID."""
    order = db.get_or_404(Order, order_id)
    return jsonify(order.to_dict()), 200


@api.route("/orders", methods=["POST"])
def create_order():
    """
    Create a new order for a customer.
    This automatically updates the customer's orders relationship in the database.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["customer_id", "items", "total_price"]
    missing = [field for field in required if data.get(field) is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Validate customer exists
    customer = db.session.get(Customer, data["customer_id"])
    if not customer:
        return jsonify({"error": f"Customer {data['customer_id']} not found"}), 404

    # Validate caterer if provided
    caterer = None
    if data.get("caterer_id"):
        caterer = db.session.get(Caterer, data["caterer_id"])
        if not caterer:
            return jsonify({"error": f"Caterer {data['caterer_id']} not found"}), 404

    try:
        total_price = float(data["total_price"])
    except (TypeError, ValueError):
        return jsonify({"error": "total_price must be a number"}), 400

    valid_statuses = {"pending", "confirmed", "delivered", "cancelled"}
    status = data.get("status", "pending")
    if status not in valid_statuses:
        return jsonify({"error": f"status must be one of: {', '.join(sorted(valid_statuses))}"}), 400

    order = Order(
        customer_id=data["customer_id"],
        caterer_id=data.get("caterer_id"),
        items=data["items"],
        total_price=total_price,
        status=status,
        notes=data.get("notes"),
    )
    db.session.add(order)
    db.session.commit()

    # Return the updated customer view alongside the new order so the caller
    # can see that the customer's orders list has been updated.
    return jsonify({
        "order": order.to_dict(),
        "customer": customer.to_dict(),
    }), 201


# ─────────────────────────────────────────────
# CATERER ROUTES
# ─────────────────────────────────────────────

@api.route("/caterers", methods=["GET"])
def get_caterers():
    """Return all caterers."""
    caterers = Caterer.query.all()
    return jsonify([c.to_dict() for c in caterers]), 200


@api.route("/caterers/<int:caterer_id>", methods=["GET"])
def get_caterer(caterer_id):
    """Return a single caterer by ID."""
    caterer = db.get_or_404(Caterer, caterer_id)
    return jsonify(caterer.to_dict()), 200


@api.route("/caterers", methods=["POST"])
def create_caterer():
    """Add a new caterer to the database."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["name", "email"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if Caterer.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "A caterer with this email already exists"}), 409

    rating = data.get("rating")
    if rating is not None:
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return jsonify({"error": "rating must be a number"}), 400

    caterer = Caterer(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        specialty=data.get("specialty"),
        rating=rating,
    )
    db.session.add(caterer)
    db.session.commit()
    return jsonify(caterer.to_dict()), 201
