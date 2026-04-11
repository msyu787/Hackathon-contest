"""사용자 관련 Pydantic 스키마 정의"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """사용자 생성 요청 스키마.

    Attributes:
        name: 사용자 이름
    """

    name: str = Field(..., min_length=1, max_length=100, description="사용자 이름")


class UserResponse(BaseModel):
    """사용자 응답 스키마.

    Attributes:
        id: 사용자 고유 ID
        name: 사용자 이름
        created_at: 생성 일시
    """

    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
