from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the Invoice model
class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    ntn = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    st_reg_no = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    customer_receipt_no = db.Column(db.Integer, nullable=False)
    customer_ntn = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(200), nullable=True)
    customer_st_reg_no = db.Column(db.String(50), nullable=False)
    customer_phone_number = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    total_amount_excluding_tax = db.Column(db.Float, nullable=False)
    total_sales_tax = db.Column(db.Float, nullable=False)
    total_amount_including_tax = db.Column(db.Float, nullable=False)

    # Relationship to products
    products = db.relationship("Product", backref="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Invoice {self.id}>'

# Define the Product model
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    price_with_tax = db.Column(db.Integer, nullable=False)
    amount_excluding_tax = db.Column(db.Float, nullable=False)
    sales_tax = db.Column(db.Float, nullable=False)
    amount_including_tax = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.id} for Invoice {self.invoice_id}>'