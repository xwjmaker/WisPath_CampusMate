from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class AIDialogSummaryOut(BaseModel):
    id: int
    student_id: int
    student_name: str = ""
    summary: str
    level: str
    keywords_matched: str | None = None
    resolved: bool
    created_at: str | datetime
    intervention_type: str | None = None
    intervention_note: str | None = None
    resolved_by: int | None = None
    resolved_at: str | datetime | None = None
    follow_up_date: str | None = None

    class Config:
        from_attributes = True


class CrisisResolve(BaseModel):
    resolved: bool = True


class CrisisInterveneIn(BaseModel):
    intervention_type: str
    intervention_note: str | None = None
    follow_up_date: str | None = None
    resolved: bool = True
