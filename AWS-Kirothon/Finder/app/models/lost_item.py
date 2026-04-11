"""분실물(LostItem) SQLAlchemy 모델 정의"""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CategoryEnum(str, enum.Enum):
    """분실물 카테고리 열거형"""

    지갑 = "지갑"
    카드 = "카드"
    신분증 = "신분증"
    전자기기 = "전자기기"
    핸드폰 = "핸드폰"
    기타 = "기타"


class StatusEnum(str, enum.Enum):
    """분실물 상태 열거형"""

    active = "active"
    pending = "pending"
    completed = "completed"


class LostItem(Base):
    """분실물 게시물 테이블 모델.

    Attributes:
        id: 게시물 고유 ID (PK, 자동 증가)
        finder_id: 발견자 ID (FK → users.id)
        category: 카테고리 (지갑/카드/신분증/전자기기/기타)
        location: 발견 장소
        found_at: 발견 시간
        image_path: 이미지 저장 경로
        caption_color: 캡션 - 색상
        caption_size: 캡션 - 크기
        caption_details: 캡션 - 세부특징
        caption_text: 매칭용 합성 텍스트
        caption_embedding: 임베딩 벡터 (직렬화)
        owner_name: 분실물 소유자 이름 (신분증류)
        status: 상태 (active/pending/completed)
        created_at: 등록 일시
    """

    __tablename__ = "lost_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    finder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    found_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption_color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    caption_size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    caption_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    caption_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    caption_embedding: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True
    )
    owner_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
