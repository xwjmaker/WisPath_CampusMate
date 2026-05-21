from pydantic import BaseModel
from datetime import datetime


class TicketCreate(BaseModel):
    type: str
    title: str
    content: str


class TicketOut(BaseModel):
    id: int
    applicant_id: int
    type: str
    title: str
    content: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketApprove(BaseModel):
    action: str
    comment: str | None = None
