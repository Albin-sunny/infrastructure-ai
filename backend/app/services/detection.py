from ultralytics import YOLO
import numpy as np

model = YOLO("models/best.pt")


def detect_crack(image_path):

    results = model.predict(
        source=image_path,
        conf=0.25,
        save=False
    )

    return results


def calculate_crack_area(results):

    if results[0].masks is None:
        return 0.0

    masks = results[0].masks.data.cpu().numpy()

    crack_pixels = np.sum(masks)

    image_height = results[0].orig_shape[0]
    image_width = results[0].orig_shape[1]

    total_pixels = image_height * image_width

    crack_percentage = (
        crack_pixels / total_pixels
    ) * 100

    return round(crack_percentage, 2)