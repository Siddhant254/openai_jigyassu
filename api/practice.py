from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from utils.file_saver import save_study_material
from utils.extraction import extract_content, extract_qr_content
from utils.vector_store import store_in_vector_db , retrieve_from_vector_db
from PIL import Image
from schemas import schemas
from models import models
from db.database import SessionLocal, engine
import io
import uuid
from sqlalchemy.orm import Session

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# In-memory map to store subject -> chapters
subject_chapter_map = {}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject: str = Form(...),
    chapter: str = Form(...),
    db: Session = Depends(get_db)
):
    # Update in-memory subject-chapter map
    if subject in subject_chapter_map:
        if chapter not in subject_chapter_map[subject]:
            subject_chapter_map[subject].append(chapter)
    else:
        subject_chapter_map[subject] = [chapter]

    try:
        # Read file content
        content = await file.read()
        file_path = save_study_material(file.filename, content)

        # Generate UUID for this material
        material_id = str(uuid.uuid4())

        extracted_text = ""

        # If image file
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(io.BytesIO(content))
            qr_code_data = extract_qr_content(image)

            if qr_code_data:
                # If QR contains a URL (future enhancement)
                if qr_code_data.startswith("http"):
                    # You can handle URL content extraction here if needed
                    # url_content = fetch_url_content(qr_code_data)
                    # extracted_text = url_content if url_content else ""
                    raise HTTPException(status_code=400, detail="QR code URL content handling not implemented yet.")
                else:
                    extracted_text = qr_code_data
            else:
                # Fallback: extract text from image
                extracted_text = extract_content(file_path)
        else:
            # PDF, TXT, etc.
            extracted_text = extract_content(file_path)

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No extractable content found in file.")

        # Store content in vector DB with metadata
        store_in_vector_db(
            extracted_text,
            metadata={
                "subject": subject,
                "chapter": chapter,
                "material_id": material_id
            }
        )

        db_material = models.StudyMaterial(
            material_id=material_id, 
            subject=subject,
            chapter=chapter,
            file_path=file_path,
            content=extracted_text
        )
        db.add(db_material)
        db.commit()
        db.refresh(db_material)

        return {
            "message": "Study material uploaded and stored successfully.",
            "material_id": material_id,
            "subject": subject,
            "chapter": chapter,
            "context": extracted_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# from fastapi import Query

# @router.get("/get-material")
# async def get_material():
#     try:
#         # Retrieve content by material_id (you can enhance filtering by subject & chapter if needed)
#         context = retrieve_from_vector_db(material_id)

#         if not context:
#             raise HTTPException(status_code=404, detail="No relevant study material found for given parameters.")

#         # Optional: You can verify metadata subject and chapter here if you store metadata alongside
#         # For example, if your vector DB returns metadata, verify subject and chapter match.

#         return {
#             "material_id": material_id,
#             "subject": subject,
#             "chapter": chapter,
#         }

@router.get("/materials", response_model=list[schemas.StudyMaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    materials = db.query(models.StudyMaterial).all()

    if not materials:
        raise HTTPException(status_code=404, detail="No study materials found")

    return materials