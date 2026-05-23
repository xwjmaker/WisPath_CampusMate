from pydantic import BaseModel
from typing import Any


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str
    college: str | None = None
    avatar: str | None = None
    skills_json: dict[str, Any] | None = None
    gender: str | None = None
    political_status: str | None = None
    title: str | None = None
    hometown: str | None = None
    phone: str | None = None
    department: str | None = None
    age: int | None = None
    tutor_id: int | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class ProfileUpdate(BaseModel):
    avatar: str | None = None
    gender: str | None = None
    political_status: str | None = None
    title: str | None = None
    hometown: str | None = None
    phone: str | None = None
    department: str | None = None
    age: int | None = None
    tutor_id: int | None = None
