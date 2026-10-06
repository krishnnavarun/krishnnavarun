import sys
import os
from PIL import Image, ImageEnhance, ImageOps

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        # Fallback search for png if jpg given or vice versa
        alt_path = input_path.rsplit('.', 1)[0] + ('.png' if input_path.endswith('.jpg') else '.jpg')
        if os.path.exists(alt_path):
            input_path = alt_path
        else:
            print(f"Error: Input photo '{input_path}' not found.")
            print("Please place a portrait photo named 'source-photo.jpg' in the repository root.")
            sys.exit(1)

    print(f"Processing photo: {input_path}...")

    # Step 1: Try rembg for background removal
    img = None
    try:
        from rembg import remove
        with open(input_path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data)
        import io
        img = Image.open(io.BytesIO(output_data)).convert('RGBA')
        print("  [✓] Background removed using rembg")
    except Exception as e:
        print(f"  [!] rembg background removal skipped or unavailable ({e}). Processing directly.")
        img = Image.open(input_path).convert('RGBA')

    # Step 2: Composite onto pure white background
    white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img).convert('L') # Convert to Grayscale

    # Step 3: Boost local contrast with OpenCV CLAHE (or PIL fallback)
    try:
        import cv2
        import numpy as np
        img_np = np.array(composited)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_np = clahe.apply(img_np)
        prepped = Image.fromarray(enhanced_np)
        print("  [✓] Local contrast enhanced using OpenCV CLAHE")
    except Exception as e:
        print(f"  [!] OpenCV CLAHE unavailable ({e}), using PIL contrast enhancement")
        enhancer = ImageEnhance.Contrast(composited)
        prepped = enhancer.enhance(1.8)
        prepped = ImageOps.autocontrast(prepped, cutoff=2)

    # Save output
    prepped.save(output_path)
    print(f"  [✓] Saved prepped photo to '{output_path}'")

if __name__ == "__main__":
    photo_file = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(photo_file)
