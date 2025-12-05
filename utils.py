from werkzeug.utils import secure_filename
from uuid import uuid4

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_filename(filename):
    ext = filename.rsplit('.', 1)[1]
    return secure_filename(f"{uuid4()}.{ext}")