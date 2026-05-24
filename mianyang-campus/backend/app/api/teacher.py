from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.growth import GrowthRecord
from app.models.crisis import AIDialogSummary
from app.models.leave import LeaveRequest
from app.models.academic import Grade
from pydantic import BaseModel

router = APIRouter(prefix="/api/teacher", tags=["teacher"])


class StudentOut(BaseModel):
    id: int
    name: str
    college: str | None = None
    username: str
    skills_json: dict | None = None
    growth_count: int = 0
    score: float = 0
    leave_count: int = 0
    crisis_level: str | None = None
    latest_crisis_summary: str | None = None
    latest_crisis_time: str | None = None
    tutor_id: int | None = None

    class Config:
        from_attributes = True


class StudentResumeOut(BaseModel):
    id: int
    name: str
    college: str | None = None
    username: str
    skills_json: dict | None = None
    growth_records: list = []

    class Config:
        from_attributes = True


class StudentDetailOut(BaseModel):
    id: int
    name: str
    college: str | None = None
    username: str
    skills_json: dict | None = None
    growth_records: list = []
    crisis_alerts: list = []
    leave_requests: list = []

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    total_students: int = 0
    alert_count: int = 0
    pending_leave_count: int = 0
    severe_alert_count: int = 0
    resolved_alert_count: int = 0

    class Config:
        from_attributes = True


def _calc_student_score(db: Session, student_id: int) -> float:
    from app.models.growth import GrowthRecord
    from app.models.crisis import AIDialogSummary
    base = 60.0
    growth_count = db.query(GrowthRecord).filter(GrowthRecord.student_id == student_id).count()
    growth_bonus = min(growth_count * 5, 30)
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    total_credit = sum(g.credit for g in grades)
    avg_gpa = sum(g.gpa * g.credit for g in grades) / total_credit if total_credit > 0 else 0
    gpa_bonus = min(avg_gpa / 4.0 * 10, 10)
    latest_crisis = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id == student_id, AIDialogSummary.resolved == False
    ).order_by(AIDialogSummary.created_at.desc()).first()
    crisis_penalty = {"severe": 20, "moderate": 10, "mild": 5}.get(
        latest_crisis.level.value if latest_crisis else "", 0
    )
    return round(max(0, min(100, base + growth_bonus + gpa_bonus - crisis_penalty)), 1)


@router.get("/dashboard", response_model=DashboardOut)
def dashboard_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if user.role != UserRole.ADMIN:
        query = query.filter(User.tutor_id == user.id)
    students = query.all()
    student_ids = [s.id for s in students]
    total = len(student_ids)
    alert_count = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1"
    ).count()
    severe_count = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.level == "severe"
    ).count()
    resolved_count = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.resolved == True
    ).count()
    pending_leave = db.query(LeaveRequest).filter(
        LeaveRequest.student_id.in_(student_ids) if student_ids else "0=1",
        LeaveRequest.status == "pending"
    ).count()
    return DashboardOut(
        total_students=total,
        alert_count=alert_count,
        pending_leave_count=pending_leave,
        severe_alert_count=severe_count,
        resolved_alert_count=resolved_count,
    )


@router.get("/students", response_model=list[StudentOut])
def list_students(
    search: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if user.role != UserRole.ADMIN:
        query = query.filter(User.tutor_id == user.id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            User.name.like(like) | User.username.like(like) | User.college.like(like)
        )
    students = query.all()
    result = []
    for s in students:
        growth_count = db.query(GrowthRecord).filter(GrowthRecord.student_id == s.id).count()
        leave_count = db.query(LeaveRequest).filter(LeaveRequest.student_id == s.id).count()
        latest_crisis = db.query(AIDialogSummary).filter(
            AIDialogSummary.student_id == s.id
        ).order_by(AIDialogSummary.created_at.desc()).first()
        score = _calc_student_score(db, s.id)
        result.append(StudentOut(
            id=s.id,
            name=s.name,
            college=s.college,
            username=s.username,
            skills_json=s.skills_json,
            growth_count=growth_count,
            score=score,
            leave_count=leave_count,
            crisis_level=latest_crisis.level.value if latest_crisis else None,
            latest_crisis_summary=latest_crisis.summary if latest_crisis else None,
            latest_crisis_time=latest_crisis.created_at.isoformat() if latest_crisis else None,
            tutor_id=s.tutor_id,
        ))
    return result


@router.get("/students/{student_id}", response_model=StudentDetailOut | StudentResumeOut)
def get_student_detail(
    student_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    student = db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    is_tutor = user.role == UserRole.ADMIN or student.tutor_id == user.id

    growth_records = db.query(GrowthRecord).filter(
        GrowthRecord.student_id == student_id
    ).order_by(GrowthRecord.date.desc()).all()

    def format_record(r):
        return {
            "id": r.id,
            "type": r.type.value if hasattr(r.type, 'value') else r.type,
            "title": r.title,
            "description": r.description,
            "date": str(r.date),
        }

    # Non-tutor teacher: resume view (growth records only)
    if not is_tutor:
        return StudentResumeOut(
            id=student.id,
            name=student.name,
            college=student.college,
            username=student.username,
            skills_json=student.skills_json,
            growth_records=[format_record(r) for r in growth_records],
        )

    # Tutor or admin: full detail view
    crisis_alerts = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id == student_id
    ).order_by(AIDialogSummary.created_at.desc()).all()

    leaves = db.query(LeaveRequest).filter(
        LeaveRequest.student_id == student_id
    ).order_by(LeaveRequest.created_at.desc()).all()

    def format_alert(a):
        return {
            "id": a.id,
            "summary": a.summary,
            "level": a.level.value if hasattr(a.level, 'value') else a.level,
            "keywords_matched": a.keywords_matched,
            "resolved": a.resolved,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }

    def format_leave(l):
        return {
            "id": l.id,
            "start_date": str(l.start_date),
            "end_date": str(l.end_date),
            "reason": l.reason,
            "leave_type": l.leave_type.value if hasattr(l.leave_type, 'value') else l.leave_type,
            "status": l.status.value if hasattr(l.status, 'value') else l.status,
            "reject_reason": l.reject_reason,
            "created_at": l.created_at.isoformat() if l.created_at else "",
        }

    return StudentDetailOut(
        id=student.id,
        name=student.name,
        college=student.college,
        username=student.username,
        skills_json=student.skills_json,
        growth_records=[format_record(r) for r in growth_records],
        crisis_alerts=[format_alert(a) for a in crisis_alerts],
        leave_requests=[format_leave(l) for l in leaves],
    )
