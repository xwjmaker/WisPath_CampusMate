from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.growth import GrowthRecord, StudentProject
from app.models.crisis import AIDialogSummary
from app.models.leave import LeaveRequest
from app.models.academic import Grade
from app.models.message import Message
from app.services.llm_service import _get_client
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/api/teacher", tags=["teacher"])


class StudentOut(BaseModel):
    id: int
    name: str
    college: str | None = None
    username: str
    avatar: str | None = None
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
    avatar: str | None = None
    skills_json: dict | None = None
    growth_records: list = []
    projects: list = []

    class Config:
        from_attributes = True


class StudentDetailOut(BaseModel):
    id: int
    name: str
    college: str | None = None
    username: str
    avatar: str | None = None
    skills_json: dict | None = None
    growth_records: list = []
    projects: list = []
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


def _calc_student_score(db: Session, student_id: int, user: User | None = None) -> float:
    from app.services.scoring import calc_radar_score
    return calc_radar_score(db, student_id, user)


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
        score = _calc_student_score(db, s.id, s)
        result.append(StudentOut(
            id=s.id,
            name=s.name,
            college=s.college,
            username=s.username,
            avatar=s.avatar,
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

    projects = db.query(StudentProject).filter(
        StudentProject.student_id == student_id
    ).order_by(StudentProject.start_date.desc()).all()

    def format_record(r):
        return {
            "id": r.id,
            "type": r.type.value if hasattr(r.type, 'value') else r.type,
            "title": r.title,
            "description": r.description,
            "date": str(r.date),
            "attachment_url": r.attachment_url,
            "honor_level": r.honor_level,
            "organizer": r.organizer,
            "competition_level": r.competition_level,
            "practice_type": r.practice_type,
            "practice_certificate": r.practice_certificate,
            "paper_type": r.paper_type,
            "paper_name": r.paper_name,
            "first_author": r.first_author,
            "second_author": r.second_author,
            "third_author": r.third_author,
            "achievement_type": r.achievement_type,
            "achievement_name": r.achievement_name,
        }

    def format_project(p):
        return {
            "id": p.id,
            "project_name": p.project_name,
            "start_date": str(p.start_date),
            "end_date": str(p.end_date) if p.end_date else None,
            "is_team": p.is_team,
            "team_members": p.team_members,
            "attachment_url": p.attachment_url,
        }

    # Non-tutor teacher: resume view (growth records only)
    if not is_tutor:
        return StudentResumeOut(
            id=student.id,
            name=student.name,
            college=student.college,
            username=student.username,
            avatar=student.avatar,
            skills_json=student.skills_json,
            growth_records=[format_record(r) for r in growth_records],
            projects=[format_project(p) for p in projects],
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
        avatar=student.avatar,
        skills_json=student.skills_json,
        growth_records=[format_record(r) for r in growth_records],
        projects=[format_project(p) for p in projects],
        crisis_alerts=[format_alert(a) for a in crisis_alerts],
        leave_requests=[format_leave(l) for l in leaves],
    )


@router.get("/growth-stats")
def growth_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if user.role != UserRole.ADMIN:
        query = query.filter(User.tutor_id == user.id)
    student_ids = [s.id for s in query.all()]
    if not student_ids:
        return {"honor": 0, "competition": 0, "practice": 0, "paper": 0, "achievement": 0}
    stats = db.query(
        GrowthRecord.type,
        func.count(GrowthRecord.id)
    ).filter(GrowthRecord.student_id.in_(student_ids)).group_by(GrowthRecord.type).all()
    result = {s[0].value: s[1] for s in stats}
    for t in ["honor", "competition", "practice", "paper", "achievement"]:
        result.setdefault(t, 0)
    return result


@router.get("/class-evaluation")
def class_evaluation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if user.role != UserRole.ADMIN:
        query = query.filter(User.tutor_id == user.id)
    students = query.all()
    student_ids = [s.id for s in students]
    total = len(student_ids)
    if total == 0:
        return {
            "total_students": 0, "avg_gpa": 0, "avg_score": 0,
            "growth": {"honor": 0, "competition": 0, "practice": 0, "paper": 0, "achievement": 0},
            "crisis": {"severe": 0, "moderate": 0, "mild": 0, "resolved": 0},
            "pending_leaves": 0,
        }

    # Average GPA
    grades = db.query(Grade).filter(Grade.student_id.in_(student_ids)).all()
    total_credit = sum(g.credit for g in grades)
    avg_gpa = round(sum(g.gpa * g.credit for g in grades) / total_credit, 2) if total_credit > 0 else 0

    # Average score
    total_score = 0
    for s in student_ids:
        total_score += _calc_student_score(db, s)
    avg_score = round(total_score / total, 1)

    # Growth records
    growth = db.query(
        GrowthRecord.type,
        func.count(GrowthRecord.id)
    ).filter(GrowthRecord.student_id.in_(student_ids) if student_ids else "0=1"
    ).group_by(GrowthRecord.type).all()
    growth_data = {r[0].value: r[1] for r in growth}
    for t in ["honor", "competition", "practice", "paper", "achievement"]:
        growth_data.setdefault(t, 0)

    # Crisis by level
    crisis_severe = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.level == "severe",
    ).count()
    crisis_moderate = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.level == "moderate",
    ).count()
    crisis_mild = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.level == "mild",
    ).count()
    crisis_resolved = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id.in_(student_ids) if student_ids else "0=1",
        AIDialogSummary.resolved == True,
    ).count()

    pending_leaves = db.query(LeaveRequest).filter(
        LeaveRequest.student_id.in_(student_ids) if student_ids else "0=1",
        LeaveRequest.status == "pending",
    ).count()

    return {
        "total_students": total,
        "avg_gpa": avg_gpa,
        "avg_score": avg_score,
        "growth": growth_data,
        "crisis": {
            "severe": crisis_severe,
            "moderate": crisis_moderate,
            "mild": crisis_mild,
            "resolved": crisis_resolved,
        },
        "pending_leaves": pending_leaves,
    }


class ContactSuggestionOut(BaseModel):
    student_id: int
    student_name: str
    reason: str
    priority: str


@router.get("/suggest-contacts", response_model=list[ContactSuggestionOut])
def suggest_contacts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")

    # 获取教师名下学生
    query = db.query(User).filter(User.role == UserRole.STUDENT)
    if user.role != UserRole.ADMIN:
        query = query.filter(User.tutor_id == user.id)
    students = query.all()
    if not students:
        return []

    # 收集每个学生的相关信息
    student_infos = []
    for s in students:
        # 最近联系时间
        last_msg = db.query(Message).filter(
            ((Message.sender_id == user.id) & (Message.receiver_id == s.id)) |
            ((Message.sender_id == s.id) & (Message.receiver_id == user.id))
        ).order_by(Message.created_at.desc()).first()
        last_contact = last_msg.created_at.isoformat() if last_msg else "从未联系"

        # 危机预警
        latest_crisis = db.query(AIDialogSummary).filter(
            AIDialogSummary.student_id == s.id
        ).order_by(AIDialogSummary.created_at.desc()).first()

        # 成长记录数
        growth_count = db.query(GrowthRecord).filter(GrowthRecord.student_id == s.id).count()

        # 请假记录
        leave_count = db.query(LeaveRequest).filter(LeaveRequest.student_id == s.id).count()

        student_infos.append({
            "id": s.id,
            "name": s.name,
            "college": s.college or "未分配",
            "last_contact": last_contact,
            "crisis_level": latest_crisis.level.value if latest_crisis else None,
            "growth_count": growth_count,
            "leave_count": leave_count,
        })

    # 构造 prompt 发送给 AI
    students_text = "\n".join([
        f"- {info['name']}（{info['college']}）：最近联系={info['last_contact']}，危机等级={info['crisis_level'] or '无'}，成果数={info['growth_count']}，请假数={info['leave_count']}，ID={info['id']}"
        for info in student_infos
    ])

    prompt = f"""你是校园管理助手。请从以下学生名单中，分析并推荐3位最应该主动联系的学生。

学生信息：
{students_text}

分析维度：
1. 长时间未联系的学生（优先级高）
2. 有危机预警的学生（优先级高）
3. 近期请假较多的学生（需关注）
4. 有成长成果但未沟通的学生（鼓励）

要求：
1. 从列表中选出3位学生
2. 每位学生给出具体理由（至少20字）
3. 标注优先级：high/medium/low
4. 只返回JSON数组，不要其他内容

格式：[{{"student_id": 1, "student_name": "姓名", "reason": "具体理由...", "priority": "high"}}]"""

    try:
        resp = _get_client().chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        content = resp.choices[0].message.content or ""
        # 清理 markdown 代码块
        import re
        cleaned = re.sub(r"```(?:json)?\s*", "", content).strip().rstrip("`")
        result = json.loads(cleaned)
        return result
    except Exception as e:
        print(f"[AI推荐联系] 错误: {e}")
        # fallback: 返回前3个学生
        return [
            {"student_id": s["id"], "student_name": s["name"], "reason": "AI分析暂不可用，建议手动查看", "priority": "medium"}
            for s in student_infos[:3]
        ]
