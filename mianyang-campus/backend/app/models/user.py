from sqlalchemy import String, Integer, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))
    college: Mapped[str | None] = mapped_column(String(100))
    avatar: Mapped[str | None] = mapped_column(String(255))
    tutor_id: Mapped[int | None] = mapped_column(default=None)
    skills_json: Mapped[dict | None] = mapped_column(JSON, default=None)
    gender: Mapped[str | None] = mapped_column(String(10))
    political_status: Mapped[str | None] = mapped_column(String(20))
    title: Mapped[str | None] = mapped_column(String(50))
    hometown: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    department: Mapped[str | None] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer)
