from pydantic import BaseModel
from datetime import date


class GrowthRecordCreate(BaseModel):
    type: str
    title: str
    description: str | None = None
    date: str
    attachment_url: str | None = None


class GrowthRecordOut(BaseModel):
    id: int
    student_id: int
    type: str
    title: str
    description: str | None = None
    date: date
    attachment_url: str | None = None

    class Config:
        from_attributes = True
