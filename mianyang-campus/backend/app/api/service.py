from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service import ServiceTicket, TicketStatus
from app.schemas.service import TicketCreate, TicketOut, TicketApprove

router = APIRouter(prefix="/api/service", tags=["service"])


@router.post("/tickets", response_model=TicketOut)
def create_ticket(req: TicketCreate, db: Session = Depends(get_db)):
    ticket = ServiceTicket(applicant_id=1, **req.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(applicant_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ServiceTicket)
    if applicant_id:
        query = query.filter(ServiceTicket.applicant_id == applicant_id)
    if status:
        query = query.filter(ServiceTicket.status == status)
    return query.order_by(ServiceTicket.created_at.desc()).all()


@router.put("/tickets/{ticket_id}/approve")
def approve_ticket(ticket_id: int, req: TicketApprove, db: Session = Depends(get_db)):
    ticket = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    ticket.status = TicketStatus.APPROVED if req.action == "approve" else TicketStatus.REJECTED
    db.commit()
    return {"message": f"ticket {req.action}d"}
