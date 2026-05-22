from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.crisis import AIDialogSummary
from app.schemas.crisis import AIDialogSummaryOut, CrisisResolve

router = APIRouter(prefix="/api/crisis", tags=["crisis"])


@router.get("/alerts", response_model=list[AIDialogSummaryOut])
def list_alerts(resolved: bool | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(AIDialogSummary).order_by(AIDialogSummary.created_at.desc())
    if resolved is not None:
        query = query.filter(AIDialogSummary.resolved == resolved)
    alerts = query.all()
    result = []
    for a in alerts:
        student = db.query(User).filter(User.id == a.student_id).first()
        result.append(AIDialogSummaryOut(
            id=a.id,
            student_id=a.student_id,
            student_name=student.name if student else "",
            summary=a.summary,
            level=a.level.value if hasattr(a.level, 'value') else a.level,
            keywords_matched=a.keywords_matched,
            resolved=a.resolved,
            created_at=a.created_at.isoformat() if a.created_at else "",
        ))
    return result


@router.get("/students/{student_id}/alerts", response_model=list[AIDialogSummaryOut])
def list_student_alerts(student_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    alerts = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id == student_id
    ).order_by(AIDialogSummary.created_at.desc()).all()
    student = db.query(User).filter(User.id == student_id).first()
    return [
        AIDialogSummaryOut(
            id=a.id,
            student_id=a.student_id,
            student_name=student.name if student else "",
            summary=a.summary,
            level=a.level.value if hasattr(a.level, 'value') else a.level,
            keywords_matched=a.keywords_matched,
            resolved=a.resolved,
            created_at=a.created_at.isoformat() if a.created_at else "",
        ) for a in alerts
    ]


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, req: CrisisResolve, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可操作")
    alert = db.query(AIDialogSummary).filter(AIDialogSummary.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    alert.resolved = req.resolved
    db.commit()
    return {"message": "已更新"}
