from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, LoginResponse, ProfileUpdate
from app.services.auth_service import login_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, req.username, req.password)
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return result


@router.get("/teachers")
def list_teachers(db: Session = Depends(get_db)):
    teachers = db.query(User).filter(User.role == UserRole.TEACHER).all()
    from app.schemas.user import UserInfo
    return [UserInfo.model_validate(t) for t in teachers]


@router.put("/profile")
def update_profile(data: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field in ("avatar", "gender", "political_status", "title", "hometown", "phone", "department", "age", "tutor_id"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(user, field, val)
    db.commit()
    db.refresh(user)
    from app.schemas.user import UserInfo
    return UserInfo.model_validate(user)