from PIL import Image
from io import BytesIO

def process_image(file_storage, max_size=(300, 300)):
    img = Image.open(file_storage)

    # Convert to RGB to avoid PNG/CMYK/alpha issues
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize while keeping aspect ratio
    img.thumbnail(max_size)

    # Save to clean JPEG
    output = BytesIO()
    img.save(output, format="JPEG", quality=85, optimize=True)
    output.seek(0)

    return output.read(), "image/jpeg"