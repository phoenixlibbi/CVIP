from flask import Blueprint, request, render_template
from utils.models import Invoice, Product
from collections import defaultdict

base_bp = Blueprint('base', __name__)

@base_bp.route("/base")
def base():
    name = request.args.get('name')

    invoices = Invoice.query.filter_by(name=name).all()

    # Calculate total amounts
    total_amount_excl_tax = sum(invoice.total_amount_excluding_tax for invoice in invoices)
    total_sales_tax = sum(invoice.total_sales_tax for invoice in invoices)
    total_amount_incl_tax = total_amount_excl_tax + total_sales_tax

    product_quantities = defaultdict(int)
    unique_products = set()  # store unique product names

    for invoice in invoices:
        for product in invoice.products:
            product_quantities[product.product_name] += product.quantity
            unique_products.add(product.product_name)

    products = [
        {"product_name": name, "total_quantity": product_quantities[name]}
        for name in unique_products
    ]

    return render_template(
        "base.html",
        name=name,
        invoices=invoices,
        total_amount_excl_tax=total_amount_excl_tax,
        total_amount_incl_tax=total_amount_incl_tax,
        total_sales_tax=total_sales_tax,
        products=products
    )