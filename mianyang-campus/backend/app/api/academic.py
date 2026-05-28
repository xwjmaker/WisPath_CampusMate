from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.academic import Course, Grade, Exam
from app.models.user import User, UserRole
from app.schemas.academic import CourseOut, GradeOut, ExamOut

router = APIRouter(prefix="/api/academic", tags=["academic"])


@router.get("/courses", response_model=list[CourseOut])
def list_courses(
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Course)
    
    # 数据隔离
    if current_user.role == UserRole.ADMIN:
        pass  # 管理员可查看所有
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看自己名下学生的数据
        student_ids = [s.id for s in db.query(User).filter(User.tutor_id == current_user.id).all()]
        query = query.filter(Course.student_id.in_(student_ids))
    else:
        # 学生只能查看自己的数据
        query = query.filter(Course.student_id == current_user.id)
    
    # 如果指定了student_id，进一步检查权限
    if student_id:
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问其他学生的数据")
        query = query.filter(Course.student_id == student_id)
    
    return query.all()


@router.get("/grades", response_model=list[GradeOut])
def list_grades(
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Grade)
    
    # 数据隔离
    if current_user.role == UserRole.ADMIN:
        pass  # 管理员可查看所有
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看自己名下学生的数据
        student_ids = [s.id for s in db.query(User).filter(User.tutor_id == current_user.id).all()]
        query = query.filter(Grade.student_id.in_(student_ids))
    else:
        # 学生只能查看自己的数据
        query = query.filter(Grade.student_id == current_user.id)
    
    # 如果指定了student_id，进一步检查权限
    if student_id:
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问其他学生的数据")
        query = query.filter(Grade.student_id == student_id)
    
    return query.order_by(Grade.semester.desc()).all()


@router.get("/exams", response_model=list[ExamOut])
def list_exams(
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Exam)
    
    # 数据隔离
    if current_user.role == UserRole.ADMIN:
        pass  # 管理员可查看所有
    elif current_user.role == UserRole.TEACHER:
        # 教师只能查看自己名下学生的数据
        student_ids = [s.id for s in db.query(User).filter(User.tutor_id == current_user.id).all()]
        query = query.filter(Exam.student_id.in_(student_ids))
    else:
        # 学生只能查看自己的数据
        query = query.filter(Exam.student_id == current_user.id)
    
    # 如果指定了student_id，进一步检查权限
    if student_id:
        if current_user.role == UserRole.STUDENT and student_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问其他学生的数据")
        query = query.filter(Exam.student_id == student_id)
    
    return query.all()
