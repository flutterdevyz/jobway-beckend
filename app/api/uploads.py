import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.api import deps
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """
    Upload a file and return its relative path.
    Only accessible by admins.
    """
    try:
        # Generate a unique filename to avoid collisions
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return {"filename": unique_filename, "url": f"uploads/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
