from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.growth import GrowthRecord
from app.models.user import User


def calc_radar_score(db: Session, student_id: int, user: User | None = None) -> float:
    if not user:
        user = db.query(User).filter(User.id == student_id).first()
    records = db.query(GrowthRecord).filter(GrowthRecord.student_id == student_id).all()
    skills_data = user.skills_json or {"skills": [], "interests": []}
    raw_skills = skills_data.get("skills", [])
    skills = [s["name"] if isinstance(s, dict) else s for s in raw_skills]
    interests = skills_data.get("interests", [])

    type_counts = defaultdict(int)
    for r in records:
        type_counts[r.type.value if hasattr(r.type, 'value') else r.type] += 1

    n_records = len(records)
    n_skills = len(skills)
    n_interests = len(interests)

    score_practice = min(100, n_records * 10 + n_skills * 8 + type_counts.get("practice", 0) * 10)
    score_innovation = min(100, type_counts.get("competition", 0) * 25 + type_counts.get("achievement", 0) * 30)
    score_academic = min(100, type_counts.get("honor", 0) * 15 + type_counts.get("paper", 0) * 30 + n_records * 3)
    score_social = min(100, n_interests * 15 + type_counts.get("practice", 0) * 15)
    score_character = min(100, (n_records + n_skills) * 8)

    total = (score_practice + score_innovation + score_academic + score_social + score_character) / 5
    return round(total, 1)
