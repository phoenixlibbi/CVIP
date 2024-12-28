import os
import cv2
import numpy as np
import onnxruntime as ort
from ultralytics import YOLO

def load_onnx_model(model_path):
    return ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])

def load_pt_model(model_path):
    return YOLO(model_path)

def preprocess_image(image_path, input_shape=(640, 640)):
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Image not found at path: {image_path}")
    image = cv2.resize(original_image, input_shape)
    image = image.astype(np.float32) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)
    return image, original_image

def run_inference_onnx(session, image):
    input_name = session.get_inputs()[0].name
    return session.run(None, {input_name: image})

def run_inference_pt(model, image_path):
    return model(image_path)

def postprocess_output_pt(results, confidence_threshold=0.5):
    boxes, scores, class_ids = [], [], []
    for result in results:
        for box in result.boxes:
            confidence = box.conf.item()
            if confidence > confidence_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                class_id = int(box.cls.item())
                boxes.append([x1, y1, x2, y2])
                scores.append(confidence)
                class_ids.append(class_id)
    return boxes, scores, class_ids

def draw_boxes(image, boxes, scores, class_ids, class_names):
    for box, score, class_id in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = map(int, box)
        if class_id < 0 or class_id >= len(class_names):
            continue
        class_name = class_names[class_id]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{class_name}: {score:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def main():
    model_dir = 'model'
    image_dir = 'uploads'
    output_dir = 'output'

    model_files = [f for f in os.listdir(model_dir) if f.endswith(('.pt', '.onnx'))]
    if not model_files:
        print("No model file found.")
        return

    # Prefer .pt over .onnx
    model_path = os.path.join(model_dir, next((f for f in model_files if f.endswith('.pt')), model_files[0]))

    image_files = os.listdir(image_dir)
    if not image_files:
        print("No image file found.")
        return
    image_path = os.path.join(image_dir, image_files[0])

    # Load model
    if model_path.endswith('.pt'):
        model = load_pt_model(model_path)
        results = run_inference_pt(model, image_path)
        boxes, scores, class_ids = postprocess_output_pt(results)
    elif model_path.endswith('.onnx'):
        session = load_onnx_model(model_path)
        image, _ = preprocess_image(image_path)
        outputs = run_inference_onnx(session, image)
        boxes, scores, class_ids = postprocess_output_pt(outputs)
    else:
        raise ValueError("Unsupported model format.")

    # Load original image for drawing
    original_image = cv2.imread(image_path)

    class_names = [
        "businessName", "buyerAddress", "buyerContact", "buyerNTN", "buyerName",
        "buyerSTN", "date", "excl", "incl", "products", "quantity", "rate",
        "sales", "serialNumber", "supplierAddress", "supplierNTN", "supplierName",
        "supplierSTN", "total", "unknown"
    ]

    draw_boxes(original_image, boxes, scores, class_ids, class_names)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.splitext(image_files[0])[0] + '__inferenced.jpg')
    cv2.imwrite(output_path, original_image)

if __name__ == "__main__":
    main()