#!/usr/bin/env python3
"""
optimize_images.py - Generate optimized image variants for web delivery.
Creates thumbnail and medium-resolution JPEG/WebP versions with EXIF stripped.
Run BEFORE build_site.py in the build pipeline.
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    print('❌ Pillow is required. Install with: pip install Pillow>=10.0.0')
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES_DIR = os.path.join(SCRIPT_DIR, 'Pictures')
OUTPUT_BASE = os.path.join(PICTURES_DIR, 'optimized')

SIZES = {
    'thumb':  800,    # Gallery grid thumbnails
    'medium': 1200,   # Lightbox / hero / bike / motivation
}

JPEG_QUALITY = {
    'thumb':  80,
    'medium': 85,
}

WEBP_QUALITY = {
    'thumb':  75,
    'medium': 80,
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def get_source_images():
    """Return list of image filenames from Pictures/ (top-level only, skip optimized/)."""
    if not os.path.isdir(PICTURES_DIR):
        return []
    images = []
    for fname in sorted(os.listdir(PICTURES_DIR)):
        fpath = os.path.join(PICTURES_DIR, fname)
        if os.path.isfile(fpath) and os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
            images.append(fname)
    return images


def needs_update(src_path, dst_path):
    """Return True if dst does not exist or is older than src."""
    if not os.path.exists(dst_path):
        return True
    return os.path.getmtime(src_path) > os.path.getmtime(dst_path)


def optimize_image(src_path, fname):
    """Generate all optimized variants for a single image."""
    stem = os.path.splitext(fname)[0]

    with Image.open(src_path) as img:
        # Convert RGBA/P to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        orig_w, orig_h = img.size

        for size_name, max_width in SIZES.items():
            # Calculate new dimensions maintaining aspect ratio
            if orig_w > max_width:
                ratio = max_width / orig_w
                new_w = max_width
                new_h = int(orig_h * ratio)
            else:
                new_w, new_h = orig_w, orig_h

            resized = img.resize((new_w, new_h), Image.LANCZOS)

            # JPEG variant
            jpeg_dir = os.path.join(OUTPUT_BASE, size_name)
            os.makedirs(jpeg_dir, exist_ok=True)
            jpeg_path = os.path.join(jpeg_dir, stem + '.jpeg')
            if needs_update(src_path, jpeg_path):
                # Save without EXIF data by creating a clean image
                clean = Image.new('RGB', resized.size)
                clean.paste(resized)
                clean.save(jpeg_path, 'JPEG',
                           quality=JPEG_QUALITY[size_name],
                           optimize=True)

            # WebP variant
            webp_dir = os.path.join(OUTPUT_BASE, size_name + '-webp')
            os.makedirs(webp_dir, exist_ok=True)
            webp_path = os.path.join(webp_dir, stem + '.webp')
            if needs_update(src_path, webp_path):
                resized.save(webp_path, 'WEBP',
                             quality=WEBP_QUALITY[size_name])


def main():
    print('🖼️  Optimizing images...')
    images = get_source_images()
    print(f'  📸 Found {len(images)} source images')

    if not images:
        print('  ⚠️  No images found in Pictures/')
        return

    for i, fname in enumerate(images):
        src_path = os.path.join(PICTURES_DIR, fname)
        optimize_image(src_path, fname)
        print(f'  [{i+1}/{len(images)}] {fname} ✓')

    print(f'  ✅ All {len(images)} images optimized → Pictures/optimized/')


if __name__ == '__main__':
    main()
