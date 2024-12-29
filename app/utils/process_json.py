import os
import json
from flask import current_app
from utils.models import db, Invoice, Product

def json_to_db():
    """
    Reads the first JSON file in the current directory, parses its content,
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
            return ", ".join(value) if len(value) > 1 else value[0] if value else ""
        return value

    try:
        # Locate JSON files
        path = 'json'
        files = [file for file in os.listdir(path) if file.endswith('.json')]
        if not files:
            current_app.info_logger.info("No JSON files found in the directory.")
            return "No JSON files found."

        # Read the first JSON file
        file_path = os.path.join(path, files[0])
        current_app.info_logger.info(f"Processing JSON file: {file_path}")
        with open(file_path, 'r') as f:
            json_data = json.load(f)

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
            total_amount_excluding_tax=sum(clean_float(x) for x in json_data.get("excl", [])),
            total_sales_tax=sum(clean_float(x) for x in json_data.get("sales", [])),
            total_amount_including_tax=sum(clean_float(x) for x in json_data.get("incl", [])),
        )

        # Add invoice to the session
        db.session.add(invoice)
        db.session.flush()  # Flush to get the invoice ID for products

        # Add products
        for product_name, quantity, rate, excl, sales, incl in zip(
            json_data.get("products", []),
            json_data.get("quantity", []),
            json_data.get("rate", []),
            json_data.get("excl", []),
            json_data.get("sales", []),
            json_data.get("incl", []),
        ):
            if not product_name:  # Skip empty product names
                continue

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

        # Commit the transaction
        db.session.commit()

        # Log success and remove the JSON file
        current_app.info_logger.info(f"Successfully processed and stored data from {file_path}.")
        # os.remove(file_path)  # Remove the processed file
        return f"Successfully processed {file_path}."

    except Exception as e:
        db.session.rollback()
        current_app.error_logger.error(f"Error processing JSON: {e}")
        return f"Error processing JSON: {e}"
