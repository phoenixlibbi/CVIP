from flask import request
from flask import Blueprint, render_template
from models import Invoice, Product
from datetime import datetime
from utils.process_json import process_json_from_file

# Create a Blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    # Run the JSON processing function
    process_result = process_json_from_file()

    # Pagination setup
    page = request.args.get('page', 1, type=int)  # Get the current page number
    per_page = request.args.get('per_page', 10, type=int)  # Number of rows per page

    # Query invoices with pagination
    invoices = Invoice.query.paginate(page=page, per_page=per_page, error_out=False)

    # Create a list of dictionaries for each invoice's products
    invoice_data = []
    for invoice in invoices.items:
        invoice_dict = {
            "id": invoice.id,
            "ntn": invoice.ntn,
            "name": invoice.name,
            "st_reg_no": invoice.st_reg_no,
            "address": invoice.address,
            "customer_receipt_no": invoice.customer_receipt_no,
            "customer_ntn": invoice.customer_ntn,
            "customer_name": invoice.customer_name,
            "customer_st_reg_no": invoice.customer_st_reg_no,
            "customer_phone_number": invoice.customer_phone_number,
            "customer_address": invoice.customer_address,
            "business_name": invoice.business_name,
            "date": invoice.date,
            "total_amount_excluding_tax": invoice.total_amount_excluding_tax,
            "total_sales_tax": invoice.total_sales_tax,
            "total_amount_including_tax": invoice.total_amount_including_tax,
            "products": [{
                "product_name": product.product_name,
                "quantity": product.quantity,
                "rate": product.rate,
                "total_price": product.quantity * product.rate
            } for product in invoice.products]
        }
        invoice_data.append(invoice_dict)
    
    return render_template(
        "dashboard.html", 
        invoices=invoice_data, 
        pagination=invoices, 
        process_result=process_result
    )
