from flask import Flask, request, render_template, send_file, Blueprint
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

invoice_bp = Blueprint('form', __name__)

@invoice_bp.route('/form', methods=["GET", "POST"])
def generate_invoice():
    if request.method == "GET":
        return render_template('form.html')  # Render the form for user input
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    table_header_style = styles["BodyText"]
    table_header_style.fontSize = 10
    table_cell_style = styles["BodyText"]
    table_cell_style.fontSize = 9

    # Extract form data
    supplier_name = request.form.get('supplier_name')
    supplier_address = request.form.get('supplier_address')
    supplier_st_no = request.form.get('supplier_st_no')
    supplier_ntn = request.form.get('supplier_ntn')

    buyer_name = request.form.get('buyer_name')
    buyer_address = request.form.get('buyer_address')
    buyer_st_no = request.form.get('buyer_st_no')
    buyer_ntn = request.form.get('buyer_ntn')
    buyer_contact = request.form.get('buyer_contact')

    business_name = request.form.get('business_name')
    serial_number = request.form.get('serial_number')
    invoice_date = request.form.get('invoice_date')

    # Parse the date for proper formatting
    if invoice_date:
        invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").strftime("%d-%m-%Y")

    # Products
    products = []
    for i in range(1, 5):
        description = request.form.get(f'product_{i}_description')
        quantity = request.form.get(f'product_{i}_quantity')
        rate = request.form.get(f'product_{i}_rate')
        amount_ex_tax = request.form.get(f'product_{i}_amount_ex_tax')
        sales_tax = request.form.get(f'product_{i}_sales_tax')
        amount_in_tax = request.form.get(f'product_{i}_amount_in_tax')
        if description:
            products.append([
                str(i),
                Paragraph(description, styles["Normal"]),
                Paragraph(quantity, styles["Normal"]) if quantity else "",
                Paragraph(f"{float(rate):,.2f}", styles["Normal"]) if rate else "",
                Paragraph(f"{float(amount_ex_tax):,.2f}", styles["Normal"]) if amount_ex_tax else "",
                Paragraph(f"{float(sales_tax):,.2f}", styles["Normal"]) if sales_tax else "",
                Paragraph(f"{float(amount_in_tax):,.2f}", styles["Normal"]) if amount_in_tax else ""
            ])

    # Add blank rows to make the table 12 rows long
    while len(products) < 12:
        products.append(["", "", "", "", "", "", ""])

    # Total amounts
    total_ex_tax = request.form.get('total_ex_tax')
    total_sales_tax = request.form.get('total_sales_tax')
    total_in_tax = request.form.get('total_in_tax')

    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)

    

    content = []

    # Header with logo
    logo_path = "static/logo.png"  # Adjust path to your logo file
    business_name_paragraph = Paragraph(f"<b>{business_name}</b>", title_style)

    header_table = Table(
        [[Image(logo_path, width=50, height=50), business_name_paragraph]],
        colWidths=[60, 480]  # Adjust column widths for proper alignment
    )
    header_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, 0), "LEFT"),  # Align image to the left
        ("ALIGN", (1, 0), (1, 0), "CENTER")  # Align business name to the center
    ]))
    content.append(header_table)
    content.append(Spacer(1, 12))

    # Title
    content.append(Paragraph("SALES TAX INVOICE", normal_style))
    content.append(Spacer(1, 12))

    # Serial and Date
    serial_date_table = Table(
        [[Paragraph(f"<b>Serial No.:</b> {serial_number}", normal_style), 
          Paragraph(f"<b>Date:</b> {invoice_date}", normal_style)]],
        colWidths=[300, 100]
    )
    serial_date_table.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT")]))
    content.append(serial_date_table)
    content.append(Spacer(1, 12))

    # Supplier Details
    content.append(Paragraph("<b>Supplier's Details:</b>", table_header_style))
    supplier_info = [
        ["Supplier's Name:", supplier_name],
        ["Address:", supplier_address],
        ["S.T. Reg. No.:", supplier_st_no],
        ["NTN:", supplier_ntn]
    ]
    for row in supplier_info:
        content.append(Paragraph(f"<b>{row[0]}</b> {row[1]}", table_cell_style))
    content.append(Spacer(1, 12))

    # Buyer Details
    content.append(Paragraph("<b>Buyer's Details:</b>", table_header_style))
    buyer_info = [
        ["Buyer's Name:", buyer_name],
        ["Address:", buyer_address],
        ["S.T. Reg. No.:", buyer_st_no],
        ["NTN:", buyer_ntn],
        ["Contact No.:", buyer_contact]
    ]
    for row in buyer_info:
        content.append(Paragraph(f"<b>{row[0]}</b> {row[1]}", table_cell_style))
    content.append(Spacer(1, 12))

    # Product Table
    table_data = [
        [Paragraph("SR. NO."), Paragraph("Description"), Paragraph("Quantity"), Paragraph("Rate"), Paragraph("Amount Excluding ST"), Paragraph("Sales Tax"), Paragraph("Amount Including ST")]
    ] + products
    product_table = Table(table_data, colWidths=[50, 180, 50, 60, 80, 80, 80])
    product_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT")
    ]))
    content.append(product_table)
    content.append(Spacer(1, 12))

    # Footer
    footer_data = [
        [Paragraph(f"<b>Sales Tax:</b> {total_sales_tax}", normal_style),
         Paragraph("<b>Signature:</b> ___________________", normal_style)],
        [Paragraph(f"<b>Net Tax Inclusive Value:</b> {total_in_tax}", normal_style),
         Paragraph("<b>Name and Designation:</b> ___________________", normal_style)]
    ]
    footer_table = Table(footer_data, colWidths=[285, 285])
    footer_table.setStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica")
    ])
    content.append(footer_table)

    # Build PDF
    doc.build(content)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="invoice.pdf", mimetype="application/pdf")
