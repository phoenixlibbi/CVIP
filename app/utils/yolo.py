import cv2
import numpy as np
import onnxruntime as ort

def load_onnx_model(model_path):
    """
    Load the YOLO model from an ONNX file.

    Args:
        model_path (str): Path to the ONNX model file.

    Returns:
        session: ONNX runtime inference session.
    """
    # Create an ONNX runtime session
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    return session

def preprocess_image(image_path, input_shape=(640, 640)):
    """
    Preprocess the input image for YOLO model.

    Args:
        image_path (str): Path to the input image.
        input_shape (tuple): Model input shape (height, width).

    Returns:
        image (np.ndarray): Preprocessed image.
        original_image (np.ndarray): Original image for visualization.
    """
    # Load the image
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Image not found at path: {image_path}")

    # Resize and normalize the image
    image = cv2.resize(original_image, input_shape)
    image = image.astype(np.float32) / 255.0  # Normalize to [0, 1]
    image = np.transpose(image, (2, 0, 1))  # Change to CHW format
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image, original_image

def run_inference(session, image):
    """
    Run inference using the ONNX model.

    Args:
        session: ONNX runtime session.
        image (np.ndarray): Preprocessed input image.

    Returns:
        outputs: Model outputs.
    """
    # Get input name
    input_name = session.get_inputs()[0].name

    # Run inference
    outputs = session.run(None, {input_name: image})
    return outputs

def postprocess_output(outputs, confidence_threshold=0.5):
    """
    Postprocess the model outputs to get bounding boxes, scores, and class IDs.

    Args:
        outputs: Model outputs.
        confidence_threshold (float): Confidence threshold for filtering detections.

    Returns:
        boxes (list): List of bounding boxes.
        scores (list): List of confidence scores.
        class_ids (list): List of class IDs.
    """
    # Example: Assuming the output is in the format [batch, num_detections, 6]
    # where each detection is [x1, y1, x2, y2, confidence, class_id]
    detections = outputs[0][0]

    # Filter detections based on confidence threshold
    boxes = []
    scores = []
    class_ids = []
    for detection in detections:
        confidence = detection[4]
        if confidence > confidence_threshold:
            x1, y1, x2, y2 = detection[:4]
            class_id = detection[5]
            boxes.append([x1, y1, x2, y2])
            scores.append(float(confidence))
            class_ids.append(int(class_id))

    return boxes, scores, class_ids

def draw_boxes(image, boxes, scores, class_ids, class_names):
    """
    Draw bounding boxes on the image.

    Args:
        image (np.ndarray): Original image.
        boxes (list): List of bounding boxes.
        scores (list): List of confidence scores.
        class_ids (list): List of class IDs.
        class_names (list): List of class names.
    """
    print("Class IDs:", class_ids)  # Debug: Print class IDs
    for box, score, class_id in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = map(int, box)

        # Adjust for one-indexed class IDs (if necessary)
        class_id = class_id - 1  # Subtract 1 to convert to zero-indexed

        # Handle invalid class IDs
        if class_id < 0 or class_id >= len(class_names):
            print(f"Warning: Invalid class ID {class_id + 1}. Skipping this detection.")
            continue  # Skip this detection

        class_name = class_names[class_id]

        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw label
        label = f"{class_name}: {score:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def main():
    # Paths
    model_path = "best.onnx"
    image_path = "test.jpeg"

    # Load the ONNX model
    session = load_onnx_model(model_path)

    # Preprocess the image
    image, original_image = preprocess_image(image_path)

    # Run inference
    outputs = run_inference(session, image)

    # Postprocess the outputs
    boxes, scores, class_ids = postprocess_output(outputs)

    # Draw bounding boxes on the image
    class_names = [
    "businessName",
    "buyerAddress",
    "buyerContact",
    "buyerNTN",
    "buyerName",
    "buyerSTN",
    "date",
    "excl",
    "incl",
    "products",
    "quantity",
    "rate",
    "sales",
    "serialNumber",
    "supplierAddress",
    "supplierNTN",
    "supplierName",
    "supplierSTN",
    "total",
    "SRNO"
]

    draw_boxes(original_image, boxes, scores, class_ids, class_names)

    # Save or display the result
    cv2.imwrite("output.jpg", original_image)
    cv2.imshow("Output", original_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()