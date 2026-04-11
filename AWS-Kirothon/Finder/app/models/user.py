"""사용자(User) SQLAlchemy 모델 정의"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """사용자 테이블 모델.

    Attributes:
        id: 사용자 고유 ID (PK, 자동 증가)
        name: 사용자 이름
        created_at: 가입 일시
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
