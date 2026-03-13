import cv2
import numpy as np
import os
import argparse

def refine_purification(image_path, output_path):
    print(f"--- FluxEraser Pro Engine: Analyzing {os.path.basename(image_path)} ---")
    
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return

    h, w, _ = img.shape
    
    # 1. Target the bottom 40% where watermarks usually reside
    roi_start = int(h * 0.6)
    roi = img[roi_start:h, :]
    
    # 2. Advanced Mask Detection
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Use Adaptive Thresholding to catch the text regardless of floor brightness
    # It looks for local brightness peaks (like white text on blue floor)
    mask_roi = cv2.adaptiveThreshold(
        gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 15, -10
    )
    
    # Clean up the mask: Remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Connect letters together (Closing)
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
    mask_roi = cv2.morphologyEx(mask_roi, cv2.MORPH_CLOSE, close_kernel)
    
    # Dilate slightly to ensure we cover the faint edges of the font
    mask_roi = cv2.dilate(mask_roi, kernel, iterations=2)

    # 3. Create global mask
    full_mask = np.zeros((h, w), dtype=np.uint8)
    full_mask[roi_start:h, :] = mask_roi
    
    # Soften mask edges for better blending
    full_mask = cv2.GaussianBlur(full_mask, (5, 5), 0)
    _, full_mask = cv2.threshold(full_mask, 128, 255, cv2.THRESH_BINARY)

    # 4. Multi-Pass AI Inpainting
    print("AI Reconstruction Phase 1 (Core Removal)...")
    # NS (Navier-Stokes) is great for preserved fluid textures like your swirly floor
    clean = cv2.inpaint(img, full_mask, 7, cv2.INPAINT_NS)
    
    print("AI Reconstruction Phase 2 (Edge Blending)...")
    # Fine-tune the edges with TELEA
    clean = cv2.inpaint(clean, full_mask, 3, cv2.INPAINT_TELEA)

    # 5. Save the result
    cv2.imwrite(output_path, clean)
    print(f"Purification Complete! Result saved: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    refine_purification(args.input, args.output)
