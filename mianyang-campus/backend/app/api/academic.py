from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.academic import Course, Grade, Exam
from app.schemas.academic import CourseOut, GradeOut, ExamOut

router = APIRouter(prefix="/api/academic", tags=["academic"])


@router.get("/courses", response_model=list[CourseOut])
def list_courses(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.student_id == student_id).all()


@router.get("/grades", response_model=list[GradeOut])
def list_grades(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.semester.desc()).all()


@router.get("/exams", response_model=list[ExamOut])
def list_exams(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Exam).filter(Exam.student_id == student_id).all()
