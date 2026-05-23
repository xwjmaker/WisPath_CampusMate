import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api", tags=["upload"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED_TYPES = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".pdf", ".doc", ".docx", ".zip", ".rar"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {ext}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / save_name
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    return JSONResponse({"url": f"/uploads/{save_name}", "filename": file.filename})
