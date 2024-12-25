from flask import request
from flask import Blueprint, render_template
from models import Invoice, Product
from datetime import datetime

# Create a Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    invoices = Invoice.query.paginate(page=page, per_page=per_page, error_out=False)

    invoice_data = []
    for invoice in invoices.items:
        # Parse the date string into a datetime object
        invoice_date = datetime.strptime(invoice.date, '%Y-%m-%d')

        invoice_dict = {
            "id": invoice.id,
            "customer_receipt_no": invoice.customer_receipt_no,
            "business_name": invoice.business_name,
            "name": invoice.name,
            "address": invoice.address,
            "customer_name": invoice.customer_name,
            "date": invoice_date.strftime('%Y-%m-%d'),  # Format as string
            "products": [{
                "product_name": product.product_name,
                "quantity": product.quantity,
                "rate": product.rate,
                "total_price": product.quantity * product.rate
            } for product in invoice.products]
        }
        invoice_data.append(invoice_dict)
    
    return render_template("dashboard.html", invoices=invoice_data, pagination=invoices)