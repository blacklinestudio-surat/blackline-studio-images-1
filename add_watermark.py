#!/usr/bin/env python3
"""
Script to add watermarks and generate thumbnails for all images in the repository.
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


def create_watermark(logo_path, image_width, opacity=0.55):
    """
    Create a watermark composite (logo + text) with specified opacity.
    
    Args:
        logo_path: Path to the logo image file
        image_width: Width of the target image (to scale watermark appropriately)
        opacity: Opacity level (0.0 to 1.0)
    
    Returns:
        PIL Image object with transparent background containing the watermark
    """
    # Calculate watermark size (10-15% of image width, using 12% as medium)
    watermark_width = int(image_width * 0.20)
    
    # Load and resize logo
    try:
        logo = Image.open(logo_path)
        # Convert logo to RGBA if needed
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Calculate logo size maintaining aspect ratio
        logo_aspect = logo.width / logo.height
        logo_new_width = int(watermark_width * 0.8)  # Logo takes 80% of watermark width
        logo_new_height = int(logo_new_width / logo_aspect)
        logo = logo.resize((logo_new_width, logo_new_height), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Error loading logo: {e}")
        sys.exit(1)
    
    # Create text "Blackline Studio"
    text = "Blackline Studio"
    # Estimate text size (will be adjusted based on available width)
    text_size = int(watermark_width * 0.15)  # Font size relative to watermark width
    
    # Try to load a nice font, fallback to default
    try:
        # Try common system fonts
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            'C:/Windows/Fonts/arial.ttf',
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, text_size)
                    break
                except:
                    continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Create a temporary image to measure text size
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Adjust font size if text is too wide
    if text_width > watermark_width:
        text_size = int(text_size * (watermark_width / text_width) * 0.9)
        try:
            if font != ImageFont.load_default():
                font = ImageFont.truetype(font.path if hasattr(font, 'path') else font_paths[0], text_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        # Re-measure
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    # Calculate total watermark dimensions
    padding = int(watermark_width * 0.1)
    spacing = int(watermark_width * 0.05)  # Space between logo and text
    watermark_height = logo.height + spacing + text_height + (padding * 2)
    watermark_width_final = max(logo.width, text_width) + (padding * 2)
    
    # Create watermark image with transparent background
    watermark = Image.new('RGBA', (watermark_width_final, watermark_height), (0, 0, 0, 0))
    
    # Paste logo
    logo_x = (watermark_width_final - logo.width) // 2
    logo_y = padding
    watermark.paste(logo, (logo_x, logo_y), logo)
    
    # Add text
    draw = ImageDraw.Draw(watermark)
    text_x = (watermark_width_final - text_width) // 2
    text_y = logo_y + logo.height + spacing
    
    # Draw text with white color and shadow for visibility
    # Draw shadow (slightly offset) - use full opacity for shadow, will be adjusted globally
    shadow_offset = 1
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
              fill=(0, 0, 0, 200), font=font)  # Dark shadow with good visibility
    # Draw main text with full opacity (will be adjusted globally)
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Apply opacity to the entire watermark (including logo and text)
    # This ensures consistent opacity across all watermark elements
    alpha = watermark.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    watermark.putalpha(alpha)
    
    return watermark


def apply_watermark(image, watermark, position='top_right', padding=20):
    """
    Apply watermark to an image at the specified position.
    
    Args:
        image: PIL Image object
        watermark: PIL Image object (watermark)
        position: Position string ('top_right', 'top_left', 'bottom_right', 'bottom_left', 'center')
        padding: Padding from edges in pixels
    
    Returns:
        PIL Image object with watermark applied
    """
    # Ensure image is in RGBA mode
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a copy to work with
    watermarked = image.copy()
    
    # Calculate watermark position
    img_width, img_height = watermarked.size
    wm_width, wm_height = watermark.size
    
    if position == 'top_right':
        x = img_width - wm_width - padding
        y = padding
    elif position == 'top_left':
        x = padding
        y = padding
    elif position == 'bottom_right':
        x = img_width - wm_width - padding
        y = img_height - wm_height - padding
    elif position == 'bottom_left':
        x = padding
        y = img_height - wm_height - padding
    else:  # center
        x = (img_width - wm_width) // 2
        y = (img_height - wm_height) // 2
    
    # Paste watermark onto image
    watermarked.paste(watermark, (x, y), watermark)
    
    return watermarked


def process_image(image_path, logo_path, thumbnail_width=400):
    """
    Process a single image: add watermark and generate thumbnail.
    
    Args:
        image_path: Path to the image file
        logo_path: Path to the logo file
        thumbnail_width: Width for thumbnail generation
    """
    try:
        # Load image
        image = Image.open(image_path)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        original_mode = image.mode
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
            image = rgb_image
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create watermark
        watermark = create_watermark(logo_path, image.width, opacity=0.55)
        
        # Apply watermark to original
        watermarked_image = apply_watermark(image, watermark, position='top_right', padding=20)
        
        # Convert to RGB if saving as JPEG (JPEG doesn't support transparency)
        image_path_obj = Path(image_path)
        if image_path_obj.suffix.lower() in ['.jpg', '.jpeg']:
            if watermarked_image.mode == 'RGBA':
                rgb_image = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                rgb_image.paste(watermarked_image, mask=watermarked_image.split()[3])
                watermarked_image = rgb_image
        
        # Save watermarked original (overwrite)
        watermarked_image.save(image_path, quality=95, optimize=True)
        print(f"✓ Watermarked: {image_path}")
        
        # Generate thumbnail
        # Calculate thumbnail height maintaining aspect ratio
        aspect_ratio = image.height / image.width
        thumbnail_height = int(thumbnail_width * aspect_ratio)
        
        # Resize image for thumbnail
        thumbnail = image.resize((thumbnail_width, thumbnail_height), Image.Resampling.LANCZOS)
        
        # Create watermark for thumbnail (proportionally smaller)
        thumbnail_watermark = create_watermark(logo_path, thumbnail.width, opacity=0.55)
        
        # Apply watermark to thumbnail
        watermarked_thumbnail = apply_watermark(thumbnail, thumbnail_watermark, position='top_right', padding=10)
        
        # Generate thumbnail filename with -thumb prefix
        thumbnail_path = image_path_obj.parent / f"{image_path_obj.stem}-thumb{image_path_obj.suffix}"
        
        # Convert to RGB if saving as JPEG
        if thumbnail_path.suffix.lower() in ['.jpg', '.jpeg']:
            if watermarked_thumbnail.mode == 'RGBA':
                rgb_thumbnail = Image.new('RGB', watermarked_thumbnail.size, (255, 255, 255))
                rgb_thumbnail.paste(watermarked_thumbnail, mask=watermarked_thumbnail.split()[3])
                watermarked_thumbnail = rgb_thumbnail
        
        # Save thumbnail
        watermarked_thumbnail.save(thumbnail_path, quality=90, optimize=True)
        print(f"✓ Thumbnail: {thumbnail_path}")
        
    except Exception as e:
        print(f"✗ Error processing {image_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Add watermarks and generate thumbnails for all images in the repository'
    )
    parser.add_argument(
        '--logo',
        required=True,
        type=str,
        help='Path to the logo image file'
    )
    parser.add_argument(
        '--thumbnail-width',
        type=int,
        default=400,
        help='Width for thumbnails in pixels (default: 400)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to process (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate logo file
    logo_path = Path(args.logo)
    if not logo_path.exists():
        print(f"Error: Logo file not found: {args.logo}")
        sys.exit(1)
    
    # Find all image files
    root_path = Path(args.root)
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    image_files = []
    for ext in image_extensions:
        image_files.extend(root_path.rglob(f'*{ext}'))
    
    # Filter out thumbnail files (files with -thumb in name)
    image_files = [f for f in image_files if '-thumb' not in f.stem]
    
    if not image_files:
        print("No image files found to process.")
        sys.exit(0)
    
    print(f"Found {len(image_files)} image(s) to process.")
    print(f"Using logo: {args.logo}")
    print(f"Thumbnail width: {args.thumbnail_width}px\n")
    
    # Process each image
    for i, image_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing: {image_path}")
        process_image(image_path, logo_path, args.thumbnail_width)
    
    print(f"\n✓ Completed processing {len(image_files)} image(s).")


if __name__ == '__main__':
    main()

