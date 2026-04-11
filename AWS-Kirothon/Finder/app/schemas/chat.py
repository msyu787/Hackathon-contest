"""채팅 관련 Pydantic 스키마 정의"""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRoomCreate(BaseModel):
    """채팅방 생성 요청 스키마."""

    lost_item_id: int = Field(..., description="관련 분실물 ID")
    finder_id: int = Field(..., description="습득자 ID")
    seeker_id: int = Field(..., description="분실자 ID")


class ChatRoomResponse(BaseModel):
    """채팅방 응답 스키마."""

    id: int
    lost_item_id: int
    finder_id: int
    seeker_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    """메시지 전송 요청 스키마."""

    content: str = Field(..., min_length=1, max_length=2000, description="메시지 내용")


class ChatMessageResponse(BaseModel):
    """메시지 응답 스키마."""

    id: int
    room_id: int
    sender_id: int
    content: str
    message_type: str = "text"
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WebSocketMessage(BaseModel):
    """WebSocket 메시지 스키마."""

    type: str = Field(..., description="메시지 타입 (message / system)")
    sender_id: int | None = None
    content: str


class VerifyRequest(BaseModel):
    """본인인증 요청 스키마."""

    name: str = Field(..., description="이름")
    student_id: str = Field(..., description="학번")
    birth_date: str = Field(..., description="생년월일 (YYYY-MM-DD)")
