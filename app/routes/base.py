from flask import Blueprint, request, render_template
from utils.models import Invoice, Product
from collections import defaultdict

base_bp = Blueprint('base', __name__)

@base_bp.route("/base")
def base():
    name = request.args.get('name')  # Get the name from the query parameter

    # Query all invoices for the selected name
    invoices = Invoice.query.filter_by(name=name).all()

    # Calculate total amounts
    total_amount_excl_tax = sum(invoice.total_amount_excluding_tax for invoice in invoices)
    total_amount_incl_tax = sum(invoice.total_amount_including_tax for invoice in invoices)

    # Get all products from the invoices and aggregate their quantities
    product_quantities = defaultdict(int)  # To store total quantities for each product
    unique_products = set()  # To store unique product names

    for invoice in invoices:
        for product in invoice.products:
            product_quantities[product.product_name] += product.quantity
            unique_products.add(product.product_name)

    # Convert the aggregated data into a list of dictionaries for the template
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
        products=products
    )