# Web App

This folder contains the main Flask application for the CVIP project.

## Folder Structure

```markdown
app/
├── data/ # data.csv file
├── instance/ # Database Instance
├── json/ # JSON files exported by ocr should place here
├── logs/ # Application logs
├── model/ # Yolo model checkpoints
├── routes/ # Flask route
├── static/ # Static files (CSS, JS, images)
├── templates/ # HTML templates
├── uploads/ # Images uploaded are store here
├── utils/ # Utility functions and scripts
├── app.py # Application entry point
├── models.py # Database models
├── requirements.txt # Python dependencies
└── init.py # Initialization file for the app package
```

## Getting Started

1.  Navigate to the `app` folder:

```bash
cd CVIP/app
```

2.  Install the required dependencies:

```bash
pip install -r requirements.txt
```

3.  Run the Flask application:

```bash
    python app.py
```
