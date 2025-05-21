import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(base_dir, ".env"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

def save_study_material(filename: str, content: bytes) -> str:
    """
    Saves uploaded file to local storage.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path
