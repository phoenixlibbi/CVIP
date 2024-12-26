from flask import Flask
from flask_scss import Scss
from models import db, Invoice, Product
from utils.logging import logging_setup
from utils.process_json import process_json_from_file
from utils.seeder import seed_data
import os

# Initialize Flask app
app = Flask(__name__)
Scss(app)

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

# Define the upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Register Blueprints
from routes.upload import upload_bp
from routes.dashboard import dashboard_bp
from routes.form import invoice_bp
from routes.base import base_bp

app.register_blueprint(upload_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(base_bp)

# Configure logging
info_logger, error_logger = logging_setup()
app.info_logger = info_logger
app.error_logger = error_logger

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # csv_file_path = "data/data.csv"
        # seed_data(start=0, end=15, file_path=csv_file_path, db=db, info_logger=info_logger, error_logger=error_logger)

    app.run(debug=True)
    # app.run(debug=True, use_reloader=False)