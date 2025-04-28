from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PIL import Image
import pytesseract
from pydub import AudioSegment
import speech_recognition as sr
from io import BytesIO
import cv2
import numpy as np
import os

# Configure Tesseract OCR path (if necessary)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Main content extraction handler
def extract_content(file_path: str) -> str:
    """
    Extracts content from PDF, TXT, image (including QR code detection), and audio files.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Extracted text content.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        return extract_pdf_text_langchain(file_path)

    elif file_extension == ".txt":
        return extract_txt_text(file_path)

    elif file_extension in [".jpg", ".jpeg", ".png"]:
        return extract_image_with_qr(file_path)

    elif file_extension in [".mp3", ".wav"]:
        return extract_audio_text(file_path)

    else:
        raise ValueError("Unsupported file type")


# PDF Extraction Using LangChain
def extract_pdf_text_langchain(pdf_path: str) -> str:
    """
    Extracts text from PDF using LangChain's PyPDFLoader.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text content.
    """
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Combine content into a single string
        pdf_text = "\n".join(doc.page_content for doc in documents)

        # Split large content into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(pdf_text)

        return "\n".join(chunks)

    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


# TXT Extraction
def extract_txt_text(txt_path: str) -> str:
    """Extracts text from TXT file."""
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error extracting TXT text: {str(e)}"


# Audio Extraction (Speech-to-Text)
def extract_audio_text(audio_path: str) -> str:
    """
    Extracts text from audio files using SpeechRecognition and Pydub.
    """
    try:
        # Convert audio to WAV format (if necessary)
        file_extension = os.path.splitext(audio_path)[1].lower()
        if file_extension != ".wav":
            audio = AudioSegment.from_file(audio_path)
            audio.export("temp_audio.wav", format="wav")
            audio_path = "temp_audio.wav"

        # Perform speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Clean up temporary file
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")

        return text

    except Exception as e:
        return f"Error extracting audio text: {str(e)}"


# QR Code Detection and Extraction
def extract_qr_content(image: Image) -> str:
    """
    Detects and extracts content from a QR code image using OpenCV.

    Args:
        image (Image): The image containing the QR code (Pillow format).

    Returns:
        str: Extracted QR code content or None if no QR code is found.
    """
    try:
        # Convert Pillow image to OpenCV format (BGR)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Initialize OpenCV QR code detector
        detector = cv2.QRCodeDetector()

        # Detect and decode QR code
        data, _, _ = detector.detectAndDecode(image_cv)

        if data:
            return data  # Return QR code content (URL or text)
        else:
            return None

    except Exception as e:
        print(f"Error extracting QR content: {e}")
        return None


# Image Extraction with QR Code Detection
def extract_image_with_qr(image_path: str) -> str:
    """
    Extracts content from an image, detecting QR codes first.
    - If a QR code is detected: extracts QR content.
    - If no QR code: performs OCR on the image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Extracted QR code content or image text.
    """
    try:
        # Open the image
        img = Image.open(image_path)

        # Try to extract QR code content
        qr_content = extract_qr_content(img)

        if qr_content:
            return f"QR Code Detected: {qr_content}"
        else:
            # If no QR code → Perform regular OCR extraction
            text = pytesseract.image_to_string(img)
            return text

    except Exception as e:
        return f"Error extracting image text: {str(e)}"
