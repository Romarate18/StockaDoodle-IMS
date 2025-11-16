from flask import request
from datetime import datetime
import base64

def parse_date(value):
    """Convert string to date — accepts YYYY-MM-DD or ISO format"""
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def get_image_blob():
    """
    Extract image from:
    - multipart/form-data → file upload (field name: 'image')
    - JSON or form-data → base64 string (field name: 'image_base64')
    Returns bytes or None
    """
    # 1. File upload
    if "image" in request.files and request.files["image"].filename:
        file = request.files["image"]
        return file.read()

    # 2. Base64 from JSON or form
    raw = (
        request.form.get("image_base64") or
        (request.get_json(silent=True) or {}).get("image_base64")
    )
    if raw:
        try:
            return base64.b64decode(raw)
        except Exception:
            return None
    return None


def extract_int(value, default=None):
    """Safely convert value to int, return default on failure"""
    try:
        return int(value) if value is not None and value != "" else default
    except (TypeError, ValueError):
        return default