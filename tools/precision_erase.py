import cv2
import numpy as np
import os
import argparse

def super_clean_erase(image_path, mask_path, output_path):
    print(f"--- FluxEraser Ultra V2: Precision Deep Clean ---")
    
    img = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None or mask is None:
        print("Error: Could not load image or mask.")
        return

    # 1. Sync dimensions
    if mask.shape[:2] != img.shape[:2]:
        mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    # 2. Refine the Mask
    _, b_mask = cv2.threshold(mask, 5, 255, cv2.THRESH_BINARY)
    
    # Large Dilation to ensure we cover the "glow" around text
    img_h, img_w = img.shape[:2]
    dilation_radius = max(5, int(min(img_h, img_w) * 0.015)) 
    print(f"Applying AI Healing Radius: {dilation_radius}px")
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_radius, dilation_radius))
    refined_mask = cv2.dilate(b_mask, kernel, iterations=2)

    # 3. Pre-Process: Content Dissolve
    # We blur the area under the mask first to lower the contrast of the watermark
    # This helps the inpainter 'forget' the text and focus on the surrounding textures
    print("AI Content Dissolving...")
    temp_img = img.copy()
    blur_radius = dilation_radius * 2
    if blur_radius % 2 == 0: blur_radius += 1
    blurred_selection = cv2.medianBlur(img, blur_radius)
    
    # Apply blur only to the mask area
    img_work = np.where(refined_mask[:, :, np.newaxis] == 255, blurred_selection, img)

    # 4. Multi-Pass Inpainting
    print("AI Synthesis Pass 1 (Texture)...")
    # NS (Navier-Stokes) is better for preserving the 'flow' of swirly epoxy floors
    result = cv2.inpaint(img_work, refined_mask, dilation_radius, cv2.INPAINT_NS)
    
    print("AI Synthesis Pass 2 (Purity)...")
    # Final pass to remove any remaining artifacts
    result = cv2.inpaint(result, refined_mask, 3, cv2.INPAINT_TELEA)

    # 5. Save final result
    cv2.imwrite(output_path, result)
    print(f"SUCCESS! purified image saved: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    super_clean_erase(args.input, args.mask, args.output)
