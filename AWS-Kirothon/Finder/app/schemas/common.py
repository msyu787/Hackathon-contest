"""API 공통 응답 모델 정의"""

from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    """모든 API 응답의 공통 형식.

    Attributes:
        success: 요청 성공 여부
        data: 응답 데이터 (없을 수 있음)
        message: 한국어 메시지
    """

    success: bool
    data: Any | None = None
    message: str


class APIErrorResponse(BaseModel):
    """오류 응답 형식.

    Attributes:
        success: 항상 False
        data: 항상 None
        message: 한국어 오류 메시지
        error_code: 오류 유형 코드
    """

    success: bool = False
    data: None = None
    message: str
    error_code: str
