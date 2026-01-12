import os
import uuid
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def generate_file_path(instance, filename):
    """Generate unique file path for uploaded images."""
    ext = os.path.splitext(filename)[1].lower()
    filename = f'{uuid.uuid4()}{ext}'

    # Determine folder based on model type
    if hasattr(instance, 'recipe'):
        return os.path.join('recipes', filename)
    elif hasattr(instance, 'email'):
        return os.path.join('profiles', filename)
    return os.path.join('uploads', filename)


def process_image(image_file, max_width=1200, quality=85):
    """
    Process uploaded image:
    - Strip EXIF data
    - Resize if larger than max_width
    - Convert to RGB if necessary
    - Return processed image file
    """
    img = Image.open(image_file)

    # Convert to RGB if necessary (handles PNG with transparency, etc.)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Strip EXIF by creating new image without metadata
    data = list(img.getdata())
    img_without_exif = Image.new(img.mode, img.size)
    img_without_exif.putdata(data)
    img = img_without_exif

    # Resize if necessary
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)

    # Create new InMemoryUploadedFile
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f'{os.path.splitext(image_file.name)[0]}.jpg',
        'image/jpeg',
        output.getbuffer().nbytes,
        None,
    )


def create_thumbnail(image_file, size=300):
    """
    Create a square thumbnail from image.
    """
    img = Image.open(image_file)

    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Create square crop from center
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim

    img = img.crop((left, top, right, bottom))
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)

    return InMemoryUploadedFile(
        output,
        'ImageField',
        f'{os.path.splitext(image_file.name)[0]}_thumb.jpg',
        'image/jpeg',
        output.getbuffer().nbytes,
        None,
    )


def validate_image(image_file):
    """
    Validate image file:
    - Check file size (max 5MB)
    - Check format (jpeg, png, webp)
    Returns (is_valid, error_message)
    """
    # Check file size (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if image_file.size > max_size:
        return False, 'Image file size must be less than 5MB.'

    # Check format
    allowed_formats = ['jpeg', 'jpg', 'png', 'webp']
    try:
        img = Image.open(image_file)
        if img.format.lower() not in allowed_formats:
            return False, f'Image format must be one of: {", ".join(allowed_formats)}.'
        image_file.seek(0)  # Reset file pointer
    except Exception:
        return False, 'Invalid image file.'

    return True, None
