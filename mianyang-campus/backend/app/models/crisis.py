from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class CrisisLevel(str, enum.Enum):
    NORMAL = "normal"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class AIDialogSummary(Base):
    __tablename__ = "ai_dialog_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    summary: Mapped[str] = mapped_column(Text)
    level: Mapped[CrisisLevel] = mapped_column(SAEnum(CrisisLevel), default=CrisisLevel.NORMAL)
    keywords_matched: Mapped[str | None] = mapped_column(String(200))
    raw_snippet: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
