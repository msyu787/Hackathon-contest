"""분실물(LostItem) 관련 Pydantic 스키마 정의"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.lost_item import CategoryEnum


class LostItemCreate(BaseModel):
    """분실물 등록 요청 스키마.

    Attributes:
        category: 카테고리 (지갑/카드/신분증/전자기기/기타)
        location: 발견 장소
        found_at: 발견 시간
    """

    category: CategoryEnum = Field(..., description="분실물 카테고리")
    location: str = Field(
        ..., min_length=1, max_length=200, description="발견 장소"
    )
    found_at: datetime = Field(..., description="발견 시간")


class LostItemResponse(BaseModel):
    """분실물 응답 스키마.

    caption_embedding은 바이너리 데이터이므로 응답에서 제외한다.

    Attributes:
        id: 게시물 고유 ID
        finder_id: 발견자 ID
        category: 카테고리
        location: 발견 장소
        found_at: 발견 시간
        image_path: 이미지 경로
        caption_color: 캡션 - 색상
        caption_size: 캡션 - 크기
        caption_details: 캡션 - 세부특징
        caption_text: 매칭용 합성 텍스트
        owner_name: 소유자 이름
        status: 상태
        created_at: 등록 일시
    """

    id: int
    finder_id: int
    category: str
    location: str
    found_at: datetime
    image_path: str
    caption_color: str | None = None
    caption_size: str | None = None
    caption_details: str | None = None
    caption_text: str | None = None
    owner_name: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaptionUpdate(BaseModel):
    """캡션 수정 요청 스키마.

    Attributes:
        color: 색상
        size: 크기
        details: 세부특징
    """

    color: str = Field(..., min_length=1, max_length=100, description="색상")
    size: str = Field(..., min_length=1, max_length=100, description="크기")
    details: str = Field(..., min_length=1, description="세부특징")
