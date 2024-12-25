import pandas as pd
from models import Invoice, Product
from flask_sqlalchemy import SQLAlchemy
import logging

def seed_data(
    start: int = 0,
    end: int = 5,
    file_path: str = None,
    db: SQLAlchemy = None,
    info_logger: logging.Logger = None,
    error_logger: logging.Logger = None
) -> None:
    """
    Seed data from a CSV file into the database.

    Args:
        start (int): Start index for reading data.
        end (int): End index for reading data.
        file_path (str): Path to the CSV file.
        db: SQLAlchemy database instance.
        info_logger: Logger for informational messages.
        error_logger: Logger for error messages.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path,low_memory=False)

        # Define required columns
        required_columns = [
            "NTN", "NAME", "S.T.Reg. No", "Address", "Customer_Receipt_NO", "Customer_NTN",
            "Customer_NAME", "Customer_S.T.Reg. No", "Customer_Phone Number", "Customer_Address",
            "Business Name", "Date", "Total Amount Excluding Taxes", "Total Sales Tax @ 18%",
            "Total Amount Including Taxes"
        ]

        # Check if all required columns are present
        if not all(column in df.columns for column in required_columns):
            error_logger.error(f"CSV file is missing required columns: {file_path}")
            return

        # Iterate over the rows and insert data into the database
        for index, row in df.iloc[start:end].iterrows():
            # Create an Invoice object
            invoice = Invoice(
                ntn=row["NTN"],
                name=row["NAME"],
                st_reg_no=row["S.T.Reg. No"],
                address=row["Address"],
                customer_receipt_no=row["Customer_Receipt_NO"],
                customer_ntn=row["Customer_NTN"],
                customer_name=row["Customer_NAME"],
                customer_st_reg_no=row["Customer_S.T.Reg. No"],
                customer_phone_number=row["Customer_Phone Number"],
                customer_address=row["Customer_Address"],
                business_name=row["Business Name"],
                date=row["Date"],
                total_amount_excluding_tax=row["Total Amount Excluding Taxes"],
                total_sales_tax=row["Total Sales Tax @ 18%"],
                total_amount_including_tax=row["Total Amount Including Taxes"],
            )

            # Add the invoice to the session
            db.session.add(invoice)
            db.session.commit()

            # Add products for this invoice
            for i in range(1, 5):  # Assuming there are up to 4 products
                product_name = row[f"Product {i}"]
                if pd.notna(product_name):  # Check if the product exists
                    product = Product(
                        invoice_id=invoice.id,
                        product_name=product_name,
                        quantity=row[f"Quantity_Product_{i}"],
                        rate=row[f"Rate_Product_{i}"],
                        tax=row[f"Tax_Product_{i}"],
                        price_with_tax=row[f"Product_{i}_Price_with_Tax"],
                        amount_excluding_tax=row[f"Amount Excluding Taxes_Product_{i}"],
                        sales_tax=row[f"Sales Tax @ 18%_Product_{i}"],
                        amount_including_tax=row[f"Amount Including Taxes_Product_{i}"],
                    )
                    db.session.add(product)

            # Commit the changes
            db.session.commit()

        # Log success
        info_logger.info(f"Data from index {start} to {end} in {file_path} has been seeded into the database.")

    except Exception as e:
        # Log error
        error_logger.error(f"Error seeding data from {file_path}: {e}")