import sys
sys.path.append('/app')

from flask import Flask
from flask_scss import Scss
from utils.models import db, Invoice, Product
from utils.logs import logging_setup
from utils.process_json import json_to_db
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

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)