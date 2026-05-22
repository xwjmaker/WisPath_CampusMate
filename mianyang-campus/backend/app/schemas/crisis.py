from pydantic import BaseModel
from datetime import datetime


class AIDialogSummaryOut(BaseModel):
    id: int
    student_id: int
    student_name: str = ""
    summary: str
    level: str
    keywords_matched: str | None = None
    resolved: bool
    created_at: str | datetime

    class Config:
        from_attributes = True


class CrisisResolve(BaseModel):
    resolved: bool = True
