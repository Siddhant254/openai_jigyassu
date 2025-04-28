import os

UPLOAD_DIR = r"C:\Users\Admin\Desktop\Openai\Jigyassu_Backend\data\uploads"

def save_study_material(filename: str, content: bytes) -> str:
    """
    Saves uploaded file to local storage.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return file_path
