from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_saver import save_study_material
from utils.extraction import extract_content, extract_qr_content
from utils.vector_store import store_in_vector_db
from PIL import Image
import io

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    print("check")
    """
    Uploads and processes file (PDF, TXT, image, audio).
    - Detects QR code in images.
    - Fetches content from QR code URLs.
    - Extracts text from regular images, PDFs, and text files.
    - Stores extracted content in vector database.
    """
    content = await file.read()

    try:
        # Save the file locally
        file_path = save_study_material(file.filename, content)   ## -> file_path of uploads

        # Check if the file is an image
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(io.BytesIO(content))
            
            # Attempt to extract QR code content
            qr_code_data = extract_qr_content(image)

            if qr_code_data:
                if qr_code_data.startswith("http"):   # Check if QR content is a URL
                    # Fetch the URL content
                    #url_content = fetch_url_content(qr_code_data)
                    pass

                    # if url_content:
                    #     store_in_vector_db(url_content)
                    #     return {"message": "QR code URL content fetched and stored successfully.", 
                    #             "url": qr_code_data}
                    # else:
                    #     return {"message": "Failed to fetch content from the QR code URL."}
                
                else:
                    # Store plain text QR content
                    store_in_vector_db(qr_code_data)
                    return {"message": "QR code content stored successfully.", "qr_content": qr_code_data}

            else:
                # No QR code → process the image as regular image
                extracted_text = extract_content(file_path)
                store_in_vector_db(extracted_text)
                return {"message": "Image uploaded and processed successfully.", "text": extracted_text}

        # For non-image files (PDF, TXT, audio)
        else:
            extracted_text = extract_content(file_path)
            store_in_vector_db(extracted_text)
            return {"message": "File uploaded and processed successfully.", "text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


