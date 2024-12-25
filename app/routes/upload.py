from flask import Blueprint, request, jsonify, render_template, current_app
from datetime import datetime
import os

# Create a Blueprint for upload routes
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/', methods=["GET", "POST"])
def index():
    """Main page for App"""
    # Access loggers from the current_app context
    info_logger = current_app.info_logger
    error_logger = current_app.error_logger

    if request.method == "POST":
        if 'files' not in request.files:
            error_message = 'No files uploaded'
            error_logger.error(error_message)  # Log the error
            return jsonify({'error': error_message}), 400

        files = request.files.getlist('files')
        file_paths = []

        for file in files:
            if file.filename == '':
                continue

            # Save the file to the uploads folder
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            try:
                file.save(file_path)
                file_paths.append(file_path)
                info_logger.info(f"File uploaded successfully: {file.filename}")  # Log the success
            except Exception as e:
                error_message = f"Failed to save file {file.filename}: {e}"
                error_logger.error(error_message)  # Log the error
                return jsonify({'error': error_message}), 500

        return jsonify({'message': 'Files uploaded successfully', 'file_paths': file_paths}), 200
    else:
        return render_template('upload.html')