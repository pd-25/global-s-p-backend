
import os
import shutil
from fastapi import HTTPException, UploadFile, status
from uuid import uuid4

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_TYPES = {"image/jpeg", "image/png"}

def validate_image_file(image: UploadFile):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG and PNG images are allowed"
        )

    image.file.seek(0, 2)
    size = image.file.tell()
    image.file.seek(0)

    if size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image size must be less than 2MB"
        )

MAX_DOC_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_DOC_TYPES = {
    "application/pdf", 
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
    "image/jpeg", 
    "image/png"
}

def validate_document_file(doc: UploadFile):
    if doc.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF, DOC, DOCX, JPEG and PNG files are allowed"
        )

    doc.file.seek(0, 2)
    size = doc.file.tell()
    doc.file.seek(0)

    if size > MAX_DOC_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document size must be less than 5MB"
        )

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        os.makedirs(destination, exist_ok=True)
        file_extension = os.path.splitext(upload_file.filename)[1]
        new_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(destination, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return file_path
    finally:
        upload_file.file.close()
        
        
