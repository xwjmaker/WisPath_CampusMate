from fastapi import APIRouter, Depends

from app.core.deps import require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/test", tags=["test"])


@router.get("/teacher-only")
def teacher_only_endpoint(user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))):
    """仅教师和管理员可访问"""
    return {"message": "教师和管理员可访问", "user": user.username, "role": user.role}


@router.get("/student-only")
def student_only_endpoint(user: User = Depends(require_role(UserRole.STUDENT))):
    """仅学生可访问"""
    return {"message": "学生可访问", "user": user.username, "role": user.role}


@router.get("/admin-only")
def admin_only_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
    """仅管理员可访问"""
    return {"message": "管理员可访问", "user": user.username, "role": user.role}
