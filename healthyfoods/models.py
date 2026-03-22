from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)

db = SQLAlchemy()


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    # Relationship: one customer has many orders
    orders = db.relationship("Order", back_populates="customer", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "orders": [order.to_dict(include_customer=False) for order in self.orders],
        }


class Caterer(db.Model):
    __tablename__ = "caterers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    specialty = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    # Relationship: one caterer handles many orders
    orders = db.relationship("Order", back_populates="caterer", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "specialty": self.specialty,
            "rating": self.rating,
            "created_at": self.created_at.isoformat(),
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    caterer_id = db.Column(db.Integer, db.ForeignKey("caterers.id"), nullable=True)
    items = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(50), nullable=False, default="pending"
    )  # pending, confirmed, delivered, cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)
    updated_at = db.Column(
        db.DateTime, default=_utcnow, onupdate=_utcnow
    )

    # Relationships back to Customer and Caterer
    customer = db.relationship("Customer", back_populates="orders")
    caterer = db.relationship("Caterer", back_populates="orders")

    def to_dict(self, include_customer=True):
        data = {
            "id": self.id,
            "customer_id": self.customer_id,
            "caterer_id": self.caterer_id,
            "items": self.items,
            "total_price": self.total_price,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_customer and self.customer:
            data["customer"] = {
                "id": self.customer.id,
                "name": self.customer.name,
                "email": self.customer.email,
            }
        if self.caterer:
            data["caterer"] = {
                "id": self.caterer.id,
                "name": self.caterer.name,
                "specialty": self.caterer.specialty,
            }
        return data
