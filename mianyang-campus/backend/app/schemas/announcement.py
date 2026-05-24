from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AnnouncementOut(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str = ""
    title: str
    content: str
    urgency: str
    attachment_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    urgency: str = "normal"


class UnreadCountOut(BaseModel):
    count: int


class ScheduleOut(BaseModel):
    id: int
    date: str
    content: str

    class Config:
        from_attributes = True


class ScheduleCreate(BaseModel):
    date: str
    content: str
