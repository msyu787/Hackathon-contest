"""캡션 생성 서비스 — 이미지에서 구조화된 캡션을 생성한다."""

import os
from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.core.exceptions import UnsupportedFormatException


class StructuredCaption(BaseModel):
    """구조화된 이미지 캡션.

    Attributes:
        color: 색상 (예: "검정색")
        size: 크기 (예: "손바닥 크기")
        details: 세부특징 (예: "가죽 재질, 지퍼 있음")
    """

    color: str
    size: str
    details: str


class VisionModelBackend(ABC):
    """비전 모델 백엔드 인터페이스.

    실제 모델 통합 시 이 클래스를 상속하여 구현한다.
    """

    @abstractmethod
    def analyze_image(self, image_path: str) -> StructuredCaption:
        """이미지를 분석하여 구조화된 캡션을 반환한다."""
        ...


class StubVisionBackend(VisionModelBackend):
    """개발/테스트용 스텁 비전 모델 백엔드.

    실제 모델 호출 대신 플레이스홀더 캡션을 반환한다.
    """

    def analyze_image(self, image_path: str) -> StructuredCaption:
        return StructuredCaption(
            color="알 수 없음",
            size="알 수 없음",
            details="자동 캡션 생성 대기 중",
        )


class CaptionService:
    """캡션 생성 서비스.

    이미지 파일의 형식을 검증하고, 비전 모델을 통해 구조화된 캡션을 생성한다.
    caption_to_text로 구조화 캡션을 매칭용 단일 텍스트로 변환한다.
    """

    SUPPORTED_FORMATS: list[str] = ["jpg", "jpeg", "png", "webp"]

    def __init__(self, backend: VisionModelBackend | None = None) -> None:
        self._backend = backend or StubVisionBackend()

    def generate_caption(self, image_path: str) -> StructuredCaption:
        """이미지에서 구조화된 캡션을 생성한다.

        Args:
            image_path: 이미지 파일 경로.

        Returns:
            StructuredCaption: color, size, details 3개 필드를 포함하는 캡션.

        Raises:
            UnsupportedFormatException: 지원하지 않는 이미지 형식인 경우.
        """
        ext = os.path.splitext(image_path)[1].lstrip(".").lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatException(
                f"지원하지 않는 이미지 형식입니다. 지원 형식: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        return self._backend.analyze_image(image_path)

    def caption_to_text(self, caption: StructuredCaption) -> str:
        """구조화된 캡션을 매칭용 단일 텍스트로 변환한다.

        Args:
            caption: 구조화된 캡션 객체.

        Returns:
            "색상, 크기, 세부특징" 형태의 합성 텍스트.
        """
        return f"{caption.color}, {caption.size}, {caption.details}"
