from flask import request, g, Blueprint, render_template
from utils.models import Invoice, Product
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
    paginated_invoices = Invoice.query.paginate(page=page, per_page=per_page, error_out=False)

    # Query all invoices for the entire dataset
    all_invoices = Invoice.query.all()

    # Create a list of dictionaries for each invoice's products (for paginated data)
    paginated_invoice_data = []
    for invoice in paginated_invoices.items:
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
        paginated_invoice_data.append(invoice_dict)

    # Create a list of dictionaries for all invoices (for the entire dataset)
    all_invoice_data = []
    for invoice in all_invoices:
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
        all_invoice_data.append(invoice_dict)

    return render_template(
        "dashboard.html", 
        invoices=paginated_invoice_data,  # Paginated data for the table
        all_invoices=all_invoice_data,    # Entire dataset for JavaScript
        pagination=paginated_invoices, 
        process_result=process_result
    )