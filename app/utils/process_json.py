import os
import json
from flask import current_app
from utils.models import db, Invoice, Product

def json_to_db():
    """
    Reads all JSON files in the current directory, parses their content,
    and stores the data in the database.
    """
    def clean_float(value):
        """
        Cleans and converts a string to a float. Removes invalid characters like '/'.
        Args:
            value (str): Input value to clean and convert.
        Returns:
            float: Cleaned float value, or 0.0 if conversion fails.
        """
        try:
            # Remove invalid characters
            cleaned_value = value.replace(",", "").replace("/", "").strip()
            return float(cleaned_value)
        except ValueError:
            return 0.0

    def extract_first_or_join(value):
        """
        Extracts the first element of a list or joins elements into a single string.
        If the value is not a list, return it as is.
        Args:
            value: Input value (list or string).
        Returns:
            str: Single string representation.
        """
        if isinstance(value, list):
            return value[0] if len(value) == 1 else ", ".join(value)
        return value

    try:
        path = 'json'   # dir
        if not os.path.exists(path):
            current_app.info_logger.info("JSON directory not found.")
            return "JSON directory not found."

        files = [file for file in os.listdir(path) if file.endswith('.json')]
        if not files:
            current_app.info_logger.info("No JSON files found in the directory.")
            return "No JSON files found."

        # Process each JSON file
        for file in files:
            file_path = os.path.join(path, file)
            current_app.info_logger.info(f"Processing JSON file: {file_path}")
            with open(file_path, 'r') as f:
                json_data = json.load(f)

            # Calculate totals
            total_amount_excluding_tax = sum(clean_float(x) for x in json_data.get("excl", []))
            total_sales_tax = sum(clean_float(x) for x in json_data.get("sales", []))
            total_amount_including_tax = total_amount_excluding_tax + total_sales_tax

            # Create a new Invoice instance
            invoice = Invoice(
                ntn=json_data.get("supplierNTN", ""),
                name=json_data.get("supplierName", ""),
                st_reg_no=json_data.get("supplierSTN", ""),
                address=json_data.get("supplierAddress", ""),
                customer_receipt_no=json_data.get("serialNumber", 0),
                customer_ntn=extract_first_or_join(json_data.get("buyerNTN", "")),
                customer_name=json_data.get("buyerName", ""),
                customer_st_reg_no=json_data.get("buyerSTN", ""),
                customer_phone_number=json_data.get("buyerContact", ""),
                customer_address=json_data.get("buyerAddress", ""),
                business_name=json_data.get("businessName", [""])[0],
                date=json_data.get("date", ""),
                total_amount_excluding_tax=total_amount_excluding_tax,
                total_sales_tax=total_sales_tax,
                total_amount_including_tax=total_amount_including_tax,
            )

            db.session.add(invoice)
            db.session.flush()

            # Add products
            for product_name, quantity, rate, excl, sales, incl in zip(
                json_data.get("products", []),
                json_data.get("quantity", []),
                json_data.get("rate", []),
                json_data.get("excl", []),
                json_data.get("sales", []),
                json_data.get("incl", []),
            ):
                if product_name:  # Only create product if product_name is not empty
                    product = Product(
                        invoice_id=invoice.id,
                        product_name=product_name,
                        quantity=int(clean_float(quantity) if quantity else 0),
                        rate=int(clean_float(rate) if rate else 0),
                        tax=clean_float(sales) if sales else 0.0,
                        price_with_tax=int(clean_float(incl) if incl else 0),
                        amount_excluding_tax=clean_float(excl) if excl else 0.0,
                        sales_tax=clean_float(sales) if sales else 0.0,
                        amount_including_tax=clean_float(incl) if incl else 0.0,
                    )
                    db.session.add(product)

            db.session.commit()

            current_app.info_logger.info(f"Successfully processed and stored data from {file_path}.")
            os.remove(file_path)

        return f"Successfully processed all JSON files."

    except Exception as e:
        db.session.rollback()
        current_app.error_logger.error(f"Error processing JSON: {e}")
        return f"Error processing JSON: {e}"