from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.growth import GrowthRecord
from app.schemas.growth import GrowthRecordCreate, GrowthRecordOut

router = APIRouter(prefix="/api/growth", tags=["growth"])


@router.get("/records", response_model=list[GrowthRecordOut])
def list_records(student_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(GrowthRecord)
    if student_id:
        query = query.filter(GrowthRecord.student_id == student_id)
    return query.order_by(GrowthRecord.date.desc()).all()


@router.post("/records", response_model=GrowthRecordOut)
def create_record(req: GrowthRecordCreate, db: Session = Depends(get_db)):
    record = GrowthRecord(student_id=1, **req.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(GrowthRecord).filter(GrowthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "deleted"}
