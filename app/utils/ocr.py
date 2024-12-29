import os
import cv2
import pytesseract
import json
import re
from ultralytics import YOLO

# Preprocessing for Tesseract
def preprocess_image(cropped):
    print("Preprocessing image...")
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    resized = cv2.resize(cleaned, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized


# Extract text using Tesseract
def extract_text_from_boxes(image, boxes, labels):
    print("Extracting text from boxes...")
    extracted_data = {}
    for box, label in zip(boxes, labels):
        x1, y1, x2, y2 = map(int, box)
        print(f"Processing box: {box} with label: {label}")
        cropped = image[y1:y2, x1:x2]
        preprocessed = preprocess_image(cropped)
        try:
            print(f"Running Tesseract on label: {label}")
            # Use appropriate Tesseract config based on the label
            if label in ["quantity", "rate", "total", "excl", "incl", "sales"]:
                text = pytesseract.image_to_string(preprocessed, config='--psm 6 -c tessedit_char_whitelist=0123456789.')
            else:
                text = pytesseract.image_to_string(preprocessed, lang='eng')
            print(f"Extracted text for label '{label}': {text.strip()}")
            extracted_data.setdefault(label, []).append(text.strip())
        except Exception as e:
            print(f"Error extracting text for label '{label}': {e}")
            continue
    return extracted_data


# Clean extracted data
def clean_extracted_data(raw_data):
    print("Cleaning extracted data...")
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

    print("Cleaned data:", cleaned_data)
    return cleaned_data


# Main pipeline
def process_image(image_path, output_folder, model_path):
    print(f"Processing image: {image_path}")
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return

    # Load YOLO model and run inference
    model = YOLO(model_path)
    results = model(image)

    # Extract bounding boxes and labels
    boxes = []
    labels = []
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy().tolist()  # Convert bounding boxes to list
        labels = [model.names[int(cls)] for cls in result.boxes.cls.cpu()]  # Get class labels

    print(f"Boxes: {boxes}, Labels: {labels}")

    # Extract text using Tesseract
    extracted_text = extract_text_from_boxes(image, boxes, labels)
    print("Extracted text:", extracted_text)

    # Clean the extracted text
    cleaned_text = clean_extracted_data(extracted_text)

    # Save cleaned data to JSON file
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(output_folder, f"{image_name}__ocr.json")
    with open(json_path, "w") as f:
        json.dump(cleaned_text, f, indent=4)

    # Delete the processed image
    os.remove(image_path)
    print(f"Processed and deleted: {image_path}")
    print(f"Cleaned data saved to: {json_path}")


# Main function
def main():
    input_folder = "uploads"  # Folder containing images to process
    output_folder = "json"  # Folder to save JSON files
    model_path = "model/best.pt"  # Path to the YOLO model

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get list of image files
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('dng', 'bmp', 'tif', 'mpo', 'jpg', 'pfm', 'tiff', 'jpeg', 'webp', 'heic', 'png'))]
    if not image_files:
        print("No image files found in the input folder.")
        return

    # Process only the first image
    image_path = os.path.join(input_folder, image_files[0])
    process_image(image_path, output_folder, model_path)


if __name__ == "__main__":
    main()