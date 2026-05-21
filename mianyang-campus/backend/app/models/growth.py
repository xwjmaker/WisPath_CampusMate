from sqlalchemy import String, Text, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class RecordType(str, enum.Enum):
    HONOR = "honor"
    COMPETITION = "competition"
    AWARD = "award"
    PRACTICE = "practice"


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    type: Mapped[RecordType] = mapped_column(SAEnum(RecordType))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    date: Mapped[str] = mapped_column(Date)
    attachment_url: Mapped[str | None] = mapped_column(String(255))
