from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.growth import GrowthRecord
from app.models.user import User
from app.models.academic import Grade
from app.models.leave import LeaveRequest
from app.schemas.growth import GrowthRecordCreate, GrowthRecordOut, GrowthProfileOut, RadarDimension, MonthlyStat, GpaPoint
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/growth", tags=["growth"])


@router.get("/profile", response_model=GrowthProfileOut)
def get_growth_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sid = current_user.id
    records = db.query(GrowthRecord).filter(GrowthRecord.student_id == sid).all()
    skills_data = current_user.skills_json or {"skills": [], "interests": []}
    skills = skills_data.get("skills", [])
    interests = skills_data.get("interests", [])

    # stats by type
    type_counts = defaultdict(int)
    for r in records:
        type_counts[r.type.value if hasattr(r.type, 'value') else r.type] += 1

    type_labels = {"honor": "荣誉", "competition": "竞赛", "practice": "实践", "paper": "论文", "achievement": "成果"}
    stats_by_type = [{"name": type_labels.get(k, k), "value": v} for k, v in type_counts.items()]

    # monthly trend (last 12 months)
    monthly = defaultdict(lambda: defaultdict(int))
    for r in records:
        try:
            d = datetime.strptime(str(r.date), "%Y-%m-%d")
            key = d.strftime("%Y-%m")
            t = r.type.value if hasattr(r.type, 'value') else r.type
            monthly[key][t] += 1
        except ValueError:
            pass

    all_months = sorted(monthly.keys())[-12:] if monthly else []
    monthly_trend = []
    for m in all_months:
        for t, c in monthly[m].items():
            monthly_trend.append(MonthlyStat(month=m, count=c, type=t))

    # radar dimensions
    n_records = len(records)
    n_skills = len(skills)
    n_interests = len(interests)
    score_practice = min(100, n_records * 10 + n_skills * 8 + type_counts.get("practice", 0) * 10)
    score_innovation = min(100, type_counts.get("competition", 0) * 25 + type_counts.get("achievement", 0) * 30)
    score_academic = min(100, type_counts.get("honor", 0) * 15 + type_counts.get("paper", 0) * 30 + n_records * 3)
    score_social = min(100, n_interests * 15 + type_counts.get("practice", 0) * 15)
    score_character = min(100, (n_records + n_skills) * 8)

    radar = [
        RadarDimension(name="学术素养", value=score_academic),
        RadarDimension(name="创新能力", value=score_innovation),
        RadarDimension(name="实践能力", value=score_practice),
        RadarDimension(name="社交素养", value=score_social),
        RadarDimension(name="综合素质", value=score_character),
    ]
    total_score = round(sum(d.value for d in radar) / 5, 1)

    # gpa trend by semester
    grades = db.query(Grade).filter(Grade.student_id == sid).all()
    semester_gpa = defaultdict(list)
    for g in grades:
        semester_gpa[g.semester].append(g.gpa)
    gpa_trend = []
    for sem in sorted(semester_gpa.keys()):
        avg = round(sum(semester_gpa[sem]) / len(semester_gpa[sem]), 2)
        gpa_trend.append(GpaPoint(semester=sem, gpa=avg))

    return GrowthProfileOut(
        total_score=total_score,
        radar=radar,
        stats_by_type=stats_by_type,
        monthly_trend=monthly_trend,
        skills=skills,
        interests=interests,
        total_records=n_records,
        total_skills=n_skills,
        gpa_trend=gpa_trend,
    )


@router.get("/records", response_model=list[GrowthRecordOut])
def list_records(student_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(GrowthRecord)
    if student_id:
        query = query.filter(GrowthRecord.student_id == student_id)
    return query.order_by(GrowthRecord.date.desc()).all()


@router.post("/records", response_model=GrowthRecordOut)
def create_record(req: GrowthRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = GrowthRecord(student_id=current_user.id, **req.model_dump())
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
