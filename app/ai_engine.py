import cv2
import numpy as np
import base64
import os

def analyze_crop_health(image_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return 0, ""

    # 1. NDVI Approximation (Normalized Difference Vegetation Index)
    # Formula: (Green - Red) / (Green + Red)
    b, g, r = cv2.split(img)
    num = g.astype(float) - r.astype(float)
    den = g.astype(float) + r.astype(float)
    den[den == 0] = 0.01  # Avoid division by zero
    ndvi = (num / den) * 100
    avg_score = np.mean(ndvi)

    # 2. Generate Thermal Heatmap (COLORMAP_JET)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    
    # 3. Encode to Base64 for web display
    _, buffer = cv2.imencode('.jpg', heatmap)
    heatmap_base64 = base64.b64encode(buffer).decode('utf-8')

    # Return Score (0-100) and the Image Data
    return round(float(avg_score), 2), heatmap_base64