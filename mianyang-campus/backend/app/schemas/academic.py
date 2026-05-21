from pydantic import BaseModel
from datetime import date, time


class CourseOut(BaseModel):
    id: int
    name: str
    teacher: str
    location: str
    day_of_week: int
    start_period: int
    end_period: int
    week_start: int
    week_end: int

    class Config:
        from_attributes = True


class GradeOut(BaseModel):
    id: int
    course_name: str
    score: float
    credit: float
    gpa: float
    semester: str

    class Config:
        from_attributes = True


class ExamOut(BaseModel):
    id: int
    course_name: str
    exam_date: date
    start_time: time
    end_time: time
    location: str

    class Config:
        from_attributes = True
