"""채팅(ChatRoom, ChatMessage) SQLAlchemy 모델 정의"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChatRoom(Base):
    """채팅방 테이블 모델.

    Attributes:
        id: 채팅방 고유 ID (PK)
        lost_item_id: 관련 분실물 ID (FK → lost_items.id)
        finder_id: 습득자 ID (FK → users.id)
        seeker_id: 분실자 ID (FK → users.id)
        status: 채팅방 상태 (active / completed)
        created_at: 생성 일시
    """

    __tablename__ = "chat_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lost_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lost_items.id"), nullable=False
    )
    finder_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    seeker_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="room", order_by="ChatMessage.created_at"
    )
    lost_item = relationship("LostItem", lazy="joined")


class ChatMessage(Base):
    """채팅 메시지 테이블 모델.

    Attributes:
        id: 메시지 고유 ID (PK)
        room_id: 채팅방 ID (FK → chat_rooms.id)
        sender_id: 발신자 ID (FK → users.id)
        content: 메시지 내용
        created_at: 전송 일시
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat_rooms.id"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")
