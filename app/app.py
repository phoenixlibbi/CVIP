from flask import Flask
from flask_scss import Scss
from models import db, Todo
from utils.logging import logging_setup
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

app.register_blueprint(upload_bp)
app.register_blueprint(dashboard_bp)

info_logger, error_logger = logging_setup()
app.info_logger = info_logger
app.error_logger = error_logger

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)