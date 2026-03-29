import cv2
import numpy as np

def analyze_crop_health(image_path: str):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Image not found"}

    # Convert to float for precision
    b, g, r = cv2.split(img.astype(float))

    # NDVI Formula: (NIR - Red) / (NIR + Red)
    # Hack: In standard photos, we use Green as a proxy for NIR 
    # to show the 'Greenness' index for the hackathon demo.
    denominator = (g + r)
    denominator[denominator == 0] = 0.1  # Prevent division by zero
    ndvi = (g - r) / denominator

    # Calculate average health percentage
    health_score = np.mean(ndvi) 
    
    # Normalize score to 0-100 for the UI
    normalized_score = max(0, min(100, (health_score + 1) * 50))
    
    return round(normalized_score, 2)