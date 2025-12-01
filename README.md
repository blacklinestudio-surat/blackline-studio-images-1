# Image Watermarking and Thumbnail Generation

This script automatically adds watermarks (logo + "Blackline Studio" text) to all images in the repository and generates thumbnails for each image.

## Features

- ✅ Adds watermark to all images (logo + "Blackline Studio" text) in top-right corner
- ✅ Generates thumbnails (400px width) with watermarks
- ✅ Saves thumbnails with `-thumb` prefix (e.g., `image-thumb.jpg`)
- ✅ Processes all image formats: `.jpg`, `.jpeg`, `.png`
- ✅ Recursively processes all subdirectories
- ✅ Overwrites original images with watermarked versions

## Prerequisites

- Python 3.6 or higher
- Pillow library (PIL)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

Or install Pillow directly:
```bash
pip install Pillow
```

## Usage

### Basic Usage (Process All Images)

Run the script from the repository root directory:

```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png"
```

### Process Specific Directory

To process images in a specific directory only:

```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png" --root "Customized Interior Products"
```

### Custom Thumbnail Size

To change the thumbnail width (default is 400px):

```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png" --thumbnail-width 600
```

## Command Line Options

- `--logo` (required): Path to the logo image file
- `--thumbnail-width` (optional): Width for thumbnails in pixels (default: 400)
- `--root` (optional): Root directory to process (default: current directory)

## What the Script Does

1. **Finds all images** recursively in the specified directory (or current directory)
2. **For each image:**
   - Loads the image
   - Creates a watermark composite (logo + "Blackline Studio" text)
   - Applies watermark to top-right corner with medium opacity (55%)
   - Overwrites the original image with watermarked version
   - Generates a thumbnail (400px width, maintains aspect ratio)
   - Saves thumbnail as `{original_filename}-thumb.{extension}`

## Watermark Specifications

- **Position:** Top-right corner
- **Opacity:** Medium (55%)
- **Size:** 10-15% of image width
- **Content:** Logo image + "Blackline Studio" text below it

## Examples

### Example 1: Process all images in repository
```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png"
```

### Example 2: Process only "Chair Wooden" directory
```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png" --root "Customized Interior Products/Chair Wooden"
```

### Example 3: Generate larger thumbnails (600px)
```bash
python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png" --thumbnail-width 600
```

## Output

The script will:
- Show progress for each image being processed
- Display success messages (✓) for each watermarked image and thumbnail
- Show error messages (✗) if any image fails to process
- Print a summary at the end

Example output:
```
Found 311 image(s) to process.
Using logo: /home/ganeshram/Downloads/Adobe Express - file.png
Thumbnail width: 400px

[1/311] Processing: Customized Interior Products/Chair Wooden/IMG-20210127-WA0021.jpg
✓ Watermarked: Customized Interior Products/Chair Wooden/IMG-20210127-WA0021.jpg
✓ Thumbnail: Customized Interior Products/Chair Wooden/IMG-20210127-WA0021-thumb.jpg
...

✓ Completed processing 311 image(s).
```

## Notes

- The script automatically skips files that already have `-thumb` in their filename to avoid processing thumbnails
- Original images are overwritten with watermarked versions
- Thumbnails are saved in the same directory as the original images
- The script handles different image formats and color modes automatically

## Troubleshooting

### Error: "Logo file not found"
- Make sure the logo file path is correct
- Use absolute path if relative path doesn't work

### Error: "cannot write mode RGBA as JPEG"
- This is automatically handled by the script (converts to RGB before saving JPEGs)

### Error: "cannot identify image file"
- The image file might be corrupted or empty
- Try restoring from git: `git checkout HEAD -- path/to/image.jpg`

### Pillow not installed
- Install it: `pip install Pillow` or `pip install -r requirements.txt`

## File Structure After Processing

```
Customized Interior Products/
  └── Chair Wooden/
      ├── IMG-20210127-WA0021.jpg          (watermarked original)
      ├── IMG-20210127-WA0021-thumb.jpg    (thumbnail)
      ├── 20210411_170509.jpg              (watermarked original)
      └── 20210411_170509-thumb.jpg        (thumbnail)
```

## Quick Start

1. Make sure Pillow is installed: `pip install Pillow`
2. Run the script:
   ```bash
   python3 add_watermark.py --logo "/home/ganeshram/Downloads/Adobe Express - file.png"
   ```
3. Wait for processing to complete
4. Check the output for any errors

That's it! All images will be watermarked and thumbnails will be generated automatically.

