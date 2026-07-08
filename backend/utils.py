import os
import uuid
from werkzeug.utils import secure_filename

def save_uploaded_file(file, upload_folder):
    """
    Saves an uploaded file with a unique name.
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    session_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    unique_filename = f"{session_id}_{filename}"
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return filepath, session_id

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
