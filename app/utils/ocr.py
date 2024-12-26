import os
import cv2
import pytesseract
import json
from ultralytics import YOLO
import re


# Set Tesseract executable path if needed (for Windows)
# Uncomment and update the path if required
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Preprocessing for Tesseract
def preprocess_image(cropped):
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    resized = cv2.resize(cleaned, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized


# Extract text using Tesseract
def extract_text_from_boxes(image, boxes, labels):
    extracted_data = {}
    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = map(int, box)
        cropped = image[y1:y2, x1:x2]
        preprocessed = preprocess_image(cropped)
        try:
            text = pytesseract.image_to_string(preprocessed, lang='eng') if label not in ['quantity', 'rate'] else pytesseract.image_to_string(preprocessed, config='--psm 6 -c tessedit_char_whitelist=0123456789.')
            extracted_data.setdefault(label, []).append(text.strip())
        except Exception as e:
            print(f"Error extracting text for label '{label}': {e}")
            continue
    return extracted_data


# Clean extracted data
def clean_extracted_data(raw_data):
    cleaned_data = {}
    for key, value in raw_data.items():
        if key in ["products"]:
            cleaned_data[key] = value[0].split("\n") if value else []
            cleaned_data[key] = [item.strip() for item in cleaned_data[key] if item.strip()]
        elif key in ["quantity", "rate", "incl", "excl", "sales", "total"]:
            cleaned_data[key] = value[0].replace("\n", " ").split() if value else []
            cleaned_data[key] = [item.strip() for item in cleaned_data[key] if item.strip()]
        elif key in ["buyerSTN", "buyerNTN", "buyerAddress", "buyerName", "supplierSTN", "supplierNTN", "date", "buyerContact", "supplierAddress", "serialNumber", "supplierName"]:
            cleaned_data[key] = value[0].strip() if value and value[0].strip() else None
            if cleaned_data[key]:
                cleaned_data[key] = re.sub(r"^[^:]*:\s*", "", cleaned_data[key])
        else:
            cleaned_data[key] = value

    if all(key in cleaned_data for key in ["products", "quantity", "rate", "incl", "excl", "sales"]):
        max_len = max(len(cleaned_data[key]) for key in ["products", "quantity", "rate", "incl", "excl", "sales"])
        for key in ["products", "quantity", "rate", "incl", "excl", "sales"]:
            cleaned_data[key] += [""] * (max_len - len(cleaned_data[key]))

    return cleaned_data


# Main pipeline
def process_images_pipeline(model_path, input_folder, output_folder, conf_threshold=0.25):
    os.makedirs(output_folder, exist_ok=True)
    raw_data_folder = os.path.join(output_folder, "raw_data")
    cleaned_data_folder = os.path.join(output_folder, "cleaned_data")
    os.makedirs(raw_data_folder, exist_ok=True)
    os.makedirs(cleaned_data_folder, exist_ok=True)

    # Load YOLO model
    model = YOLO(model_path)
    results = model(input_folder, conf=conf_threshold)
    raw_data = {}
    cleaned_data = {}

    for i, result in enumerate(results):
        image = result.orig_img.copy()
        boxes = result.boxes.xyxy.cpu().numpy()
        labels = [model.names[int(cls)] for cls in result.boxes.cls.cpu()]
        if len(boxes) == 0:
            print(f"No detections for image_{i}.")
            continue

        # Extract raw text
        extracted_text = extract_text_from_boxes(image, boxes, labels)
        raw_data[f"image_{i}"] = extracted_text

        # Save raw data to individual JSON file
        raw_data_path = os.path.join(raw_data_folder, f"image_{i}_raw.json")
        with open(raw_data_path, "w") as f:
            json.dump(extracted_text, f, indent=4)

        # Clean the extracted text
        cleaned_text = clean_extracted_data(extracted_text)
        cleaned_data[f"image_{i}"] = cleaned_text

        # Save cleaned data to individual JSON file
        cleaned_data_path = os.path.join(cleaned_data_folder, f"image_{i}_cleaned.json")
        with open(cleaned_data_path, "w") as f:
            json.dump(cleaned_text, f, indent=4)

    # Save all raw data to a single JSON file
    raw_output_path = os.path.join(output_folder, "all_raw_data.json")
    with open(raw_output_path, "w") as f:
        json.dump(raw_data, f, indent=4)

    # Save all cleaned data to a single JSON file
    cleaned_output_path = os.path.join(output_folder, "all_cleaned_data.json")
    with open(cleaned_output_path, "w") as f:
        json.dump(cleaned_data, f, indent=4)

    print(f"Raw data saved to {raw_output_path}")
    print(f"Cleaned data saved to {cleaned_output_path}")


# Example Usage
model_path = "/content/best (5).pt"  # Replace with your YOLO model path
input_folder = "/content/inputs"        # Replace with your input images folder
output_folder = "/content/output"   # Replace with your desired output folder

process_images_pipeline(model_path, input_folder, output_folder)