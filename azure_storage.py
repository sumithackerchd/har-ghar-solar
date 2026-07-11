import os
import io
import uuid

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def upload_file(file):
    """Save uploaded file locally. Returns relative URL path."""
    ext       = os.path.splitext(file.filename or "upload")[1] or ".bin"
    filename  = f"{uuid.uuid4()}{ext}"
    dest      = os.path.join(UPLOAD_FOLDER, filename)
    if hasattr(file, "read"):
        with open(dest, "wb") as f:
            f.write(file.read())
    return f"/static/uploads/{filename}"