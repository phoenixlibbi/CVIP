# CVIP Folder Structure

```markdowb
CVIP/
│
├── app/
│   ├── static/                  # For CSS, JavaScript, and images (frontend assets)
│   │   ├── css/                 # Stylesheets (e.g., style.css)
│   │   ├── js/                  # JavaScript files (optional)
│   │   └── images/              # Static images (if needed for the frontend)
│   │
│   ├── templates/               # HTML templates for Flask
│   │   ├── dashboard.html       # Main dashboard page
│   │   └── upload.html          # Upload form/page
│   │
│   ├── db/                      # Database files
│   │   └── invoices.db          # SQLite database file
│   │
│   ├── routes/                  # Flask routes and API logic
│   │   ├── __init__.py          # Flask app initialization
│   │   ├── upload.py            # Handles file uploads
│   │   └── dashboard.py         # Manages dashboard and analytics
│   │
│   ├── utils/                   # Utility functions and pipeline code
│   │   ├── yolov11_pipeline.py  # YOLO + Tesseract pipeline integration
│   │   ├── ocr.py               # Tesseract OCR-related functions
│   │   └── database.py          # Database interaction utilities
│   │
│   ├── app.py                   # Main Flask app entry point
│   └── config.py                # Configurations (e.g., paths, settings)
│
├── data/                        # Data and annotation files
│   ├── annotated/               # Annotated datasets (COCO format from Roboflow)
│   │   ├── train/               # Training images and labels
│   │   ├── test/                # Testing images and labels
│   │   └── val/                 # Validation images and labels
│   │
│   ├── raw/                     # Raw images (before annotation)
│   └── excel/                   # Excel files with raw tabular data
│
├── models/                      # Trained YOLO models
│   ├── best.pt                  # YOLOv11 PyTorch model
│   └── best.onnx                # Converted ONNX model
│
├── notebooks/                   # Jupyter notebooks for experimentation
│   ├── AutoAnnotate.ipynb       # Semi-automated annotation with Roboflow
│   ├── CVIPProject.ipynb        # Main notebook for project details
│   ├── Data2PDF.ipynb           # Converts data to PDF invoices
│   ├── FINE_TUNE_YOLLOV11.ipynb # Fine-tuning the YOLO model
│   └── YOLO.ipynb               # YOLO training and evaluation
│
├── tests/                       # Unit tests for the pipeline
│   ├── test_yolov11.py          # Tests for YOLOv11 pipeline
│   ├── test_ocr.py              # Tests for OCR integration
│   └── test_routes.py           # Tests for Flask API routes
│
├── requirements.txt             # Python dependencies for the project
├── README.md                    # Project overview and setup instructions
└── .gitignore                   # Files and folders to ignore in version control
```
