#!/usr/bin/env python3
"""
Enhanced Background Removal Tool
Process images with better transparency and quality options
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from rembg import remove, new_session
from PIL import Image
import time
import numpy as np

# Configuration
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

# Available models (quality levels)
MODELS = {
    '1': {'name': 'u2net', 'description': 'Default - Good balance of speed and quality'},
    '2': {'name': 'u2netp', 'description': 'Lightweight - Faster but lower quality'},
    '3': {'name': 'u2net_human_seg', 'description': 'People - Optimized for human subjects'},
    '4': {'name': 'u2net_cloth_seg', 'description': 'Clothing - Best for fashion/clothing'},
    '5': {'name': 'isnet-general-use', 'description': 'High Quality - Best overall quality (slower)'}
}

def ensure_folders_exist():
    """Create input and output folders if they don't exist."""
    Path(INPUT_FOLDER).mkdir(exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

def get_images_to_process():
    """Get list of image files in the input folder."""
    input_path = Path(INPUT_FOLDER)
    images = []

    for file in input_path.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS:
            images.append(file)

    return sorted(images)

def ensure_transparency(image):
    """Advanced transparency fix: make near-white and semi-transparent pixels fully transparent."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    data = np.array(image)
    red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Find near-white pixels (high RGB values)
    threshold = 240
    white_pixels = (red > threshold) & (green > threshold) & (blue > threshold)
    data[white_pixels] = [255, 255, 255, 0]

    # Find near-transparent pixels and make them fully transparent
    semi_transparent = alpha < 50
    data[semi_transparent, 3] = 0

    # Clean up edges - remove semi-transparent pixels around edges
    edge_threshold = 200
    edge_pixels = (alpha > 0) & (alpha < edge_threshold)
    edge_white = edge_pixels & ((red + green + blue) / 3 > 200)
    data[edge_white, 3] = 0

    return Image.fromarray(data, 'RGBA')

def process_image_advanced(input_path, output_path, session, alpha_matting=True, only_mask=False):
    """Remove background from a single image with advanced options."""
    try:
        print(f"  Processing: {input_path.name}...", end="")
        start_time = time.time()

        # Open image
        input_image = Image.open(input_path)

        # Process with selected model and options
        output_image = remove(
            input_image,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
            only_mask=only_mask
        )

        # Ensure proper transparency
        output_image = ensure_transparency(output_image)

        # Save as PNG to preserve transparency
        output_file = output_path / f"{input_path.stem}_no_bg.png"
        output_image.save(output_file, 'PNG', optimize=True)

        elapsed = time.time() - start_time
        print(f" ✅ Done ({elapsed:.1f}s)")
        return True, output_file

    except Exception as e:
        print(f" ❌ Failed: {e}")
        return False, None

def select_model():
    """Let user select which model to use."""
    print("\n📊 Select Quality Level:")
    print("-" * 40)
    for key, model in MODELS.items():
        print(f"{key}) {model['description']}")
    print("-" * 40)

    while True:
        choice = input("Enter your choice (1-5) [default: 1]: ").strip() or '1'
        if choice in MODELS:
            return MODELS[choice]['name']
        print("Invalid choice. Please enter 1-5.")

def select_options():
    """Let user select processing options."""
    print("\n⚙️  Processing Options:")
    print("-" * 40)

    # Alpha matting option
    alpha_matting_input = input("Enable alpha matting for smoother edges? (y/n) [default: y]: ").strip().lower()
    alpha_matting = alpha_matting_input != 'n'

    # Mask only option
    mask_only_input = input("Save mask only (black/white)? (y/n) [default: n]: ").strip().lower()
    only_mask = mask_only_input == 'y'

    return alpha_matting, only_mask

def main():
    """Main processing function."""
    print("=" * 60)
    print("🎨 ENHANCED BACKGROUND REMOVAL TOOL")
    print("=" * 60)

    # Ensure folders exist
    ensure_folders_exist()

    # Get images to process
    images = get_images_to_process()

    if not images:
        print(f"\n⚠️  No images found in '{INPUT_FOLDER}' folder!")
        print(f"\n📁 Place your images in the '{INPUT_FOLDER}' folder and run this script again.")
        print(f"\nSupported formats: {', '.join(sorted(SUPPORTED_FORMATS))}")
        return

    print(f"\n📸 Found {len(images)} image(s) to process")

    # Select model
    model_name = select_model()

    # Select options
    alpha_matting, only_mask = select_options()

    print("\n" + "=" * 60)
    print(f"🚀 Processing with model: {model_name}")
    if alpha_matting:
        print("   ✓ Alpha matting enabled (smoother edges)")
    if only_mask:
        print("   ✓ Saving mask only")
    print("=" * 60)

    # Create session with selected model
    session = new_session(model_name)

    # Process each image
    output_path = Path(OUTPUT_FOLDER)
    successful = 0
    failed = 0

    start_total = time.time()

    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}]", end=" ")
        success, output_file = process_image_advanced(
            image_path,
            output_path,
            session,
            alpha_matting=alpha_matting,
            only_mask=only_mask
        )

        if success:
            successful += 1
        else:
            failed += 1

    # Summary
    total_time = time.time() - start_total
    print("\n" + "=" * 60)
    print("📊 PROCESSING COMPLETE")
    print("-" * 60)
    print(f"✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time:.1f}s")

    if successful > 0:
        print(f"\n📂 Output files saved to: {Path(OUTPUT_FOLDER).absolute()}")
        print("\n💡 Tip: Images are saved with full transparency.")
        print("   If backgrounds still appear, try:")
        print("   - Different quality level (option 5 for best quality)")
        print("   - Enable alpha matting if disabled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)