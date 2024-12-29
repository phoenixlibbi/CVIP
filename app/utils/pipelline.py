import os
import cv2
import numpy as np
from ultralytics import YOLO
import pytesseract
import json
import re
import onnxruntime as ort
from utils.process_json import json_to_db


# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


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
        text = (
            pytesseract.image_to_string(preprocessed, lang="eng")
            if label not in ["quantity", "rate"]
            else pytesseract.image_to_string(
                preprocessed, config="--psm 6 -c tessedit_char_whitelist=0123456789."
            )
        )
        extracted_data.setdefault(label, []).append(text.strip())
    raw_json_path = os.path.join("json_raw", "001__raw.json")
    os.makedirs("json_raw", exist_ok=True)
    with open(raw_json_path, "w") as f:
        json.dump(extracted_data, f, indent=4)
    return extracted_data


def clean_extracted_data(raw_data):
    cleaned_data = {}
    for key, value in raw_data.items():
        if key == "businessName":
            if value:
                # Remove "Sales Tax Invoice" and clean up newlines
                business_name = value[0].replace("\n", " ")
                cleaned_data[key] = business_name.replace("SALES TAX INVOICE", "").strip()
            else:
                cleaned_data[key] = None
        elif key in ["products"]:
            cleaned_data[key] = value[0].split("\n") if value else []
            cleaned_data[key] = [item.strip() for item in cleaned_data[key] if item.strip()]
        elif key in ["quantity", "rate", "incl", "excl", "sales", "total"]:
            # Clean numeric data
            cleaned_data[key] = value[0].replace("\n", " ").split() if value else []
            cleaned_data[key] = [
                re.sub(r"[^\d.]", "", item.replace(",", "")) for item in cleaned_data[key] if item.strip()
            ]
        elif key in [
            "buyerSTN",
            "supplierSTN",
        ]:
            cleaned_data[key] = value[0].strip() if value and value[0].strip() else None
            if cleaned_data[key]:
                # Remove unwanted characters from STN numbers
                cleaned_data[key] = re.sub(r"[^\d]", "", cleaned_data[key])
        elif key in [
            "buyerNTN",
            "buyerAddress",
            "buyerName",
            "supplierNTN",
            "date",
            "buyerContact",
            "supplierAddress",
            "serialNumber",
            "supplierName",
        ]:
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

# Load model
def load_model(model_path):
    if model_path.endswith('.pt'):
        return YOLO(model_path)
    elif model_path.endswith('.onnx'):
        return ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    else:
        raise ValueError("Unsupported model format.")

# Run inference
def run_inference(model, image_path):
    if isinstance(model, YOLO):
        results = model(image_path)
        boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
        labels = [model.names[int(cls)] for cls in results[0].boxes.cls.cpu()]
    elif isinstance(model, ort.InferenceSession):
        image, _ = preprocess_for_onnx(image_path)
        outputs = model.run(None, {model.get_inputs()[0].name: image})
        boxes, labels = process_onnx_output(outputs)
    else:
        raise ValueError("Unsupported model type.")
    return boxes, labels

# Preprocess image for ONNX
def preprocess_for_onnx(image_path, input_shape=(640, 640)):
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Image not found at path: {image_path}")
    image = cv2.resize(original_image, input_shape)
    image = image.astype(np.float32) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)
    return image, original_image

# Process ONNX output
def process_onnx_output(outputs, confidence_threshold=0.5):
    boxes, labels = [], []
    for output in outputs:
        for box in output['boxes']:
            confidence = box[4]
            if confidence > confidence_threshold:
                boxes.append(box[:4].tolist())
                labels.append(int(box[5]))
    return boxes, labels

# Draw bounding boxes
def draw_boxes(image, boxes, labels, class_names):
    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, class_names[label], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Main processing pipeline
def process_image(image_path, output_folder, model):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return

    boxes, labels = run_inference(model, image_path)
    extracted_text = extract_text_from_boxes(image, boxes, labels)
    cleaned_text = clean_extracted_data(extracted_text)

    json_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(image_path))[0]}__ocr.json")
    with open(json_path, "w") as f:
        json.dump(cleaned_text, f, indent=4)

    # os.remove(image_path)
    print(f"Processed and deleted: {image_path}")
    print(f"Cleaned data saved to: {json_path}")

# Main function
def main():
    input_folder = "uploads"
    output_folder = "json"
    model_path = "model/best.pt"

    os.makedirs(output_folder, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('jpg', 'jpeg', 'png', 'tiff', 'bmp', 'webp'))]
    if not image_files:
        print("No image files found in the input folder.")
        return

    model = load_model(model_path)
    process_image(os.path.join(input_folder, image_files[0]), output_folder, model)
    results = json_to_db()
    return results


if __name__ == "__main__":
    main()