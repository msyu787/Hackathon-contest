"""CaptionService 단위 테스트"""

import pytest

from app.core.exceptions import UnsupportedFormatException
from app.services.caption_service import (
    CaptionService,
    StructuredCaption,
    StubVisionBackend,
    VisionModelBackend,
)


class TestStructuredCaption:
    """StructuredCaption 모델 테스트."""

    def test_create_caption(self):
        caption = StructuredCaption(color="검정색", size="손바닥 크기", details="가죽 재질, 지퍼 있음")
        assert caption.color == "검정색"
        assert caption.size == "손바닥 크기"
        assert caption.details == "가죽 재질, 지퍼 있음"


class TestCaptionService:
    """CaptionService 테스트."""

    def setup_method(self):
        self.service = CaptionService()

    # --- SUPPORTED_FORMATS ---

    def test_supported_formats(self):
        assert self.service.SUPPORTED_FORMATS == ["jpg", "jpeg", "png", "webp"]

    # --- generate_caption: 형식 검증 ---

    @pytest.mark.parametrize("ext", ["jpg", "jpeg", "png", "webp"])
    def test_generate_caption_supported_formats(self, ext):
        caption = self.service.generate_caption(f"/tmp/photo.{ext}")
        assert isinstance(caption, StructuredCaption)
        assert caption.color != ""
        assert caption.size != ""
        assert caption.details != ""

    def test_generate_caption_uppercase_extension(self):
        """대문자 확장자도 지원해야 한다."""
        caption = self.service.generate_caption("/tmp/photo.JPG")
        assert isinstance(caption, StructuredCaption)

    @pytest.mark.parametrize("ext", ["gif", "bmp", "tiff", "svg", "pdf", "heic"])
    def test_generate_caption_unsupported_format_raises(self, ext):
        with pytest.raises(UnsupportedFormatException) as exc_info:
            self.service.generate_caption(f"/tmp/photo.{ext}")
        assert "지원 형식" in exc_info.value.message
        assert exc_info.value.error_code == "UNSUPPORTED_FORMAT"

    def test_generate_caption_no_extension_raises(self):
        with pytest.raises(UnsupportedFormatException):
            self.service.generate_caption("/tmp/photo")

    # --- caption_to_text ---

    def test_caption_to_text_combines_fields(self):
        caption = StructuredCaption(color="검정색", size="손바닥 크기", details="가죽 재질, 지퍼 있음")
        text = self.service.caption_to_text(caption)
        assert text == "검정색, 손바닥 크기, 가죽 재질, 지퍼 있음"

    def test_caption_to_text_single_word_fields(self):
        caption = StructuredCaption(color="파란색", size="소형", details="플라스틱")
        text = self.service.caption_to_text(caption)
        assert text == "파란색, 소형, 플라스틱"

    # --- 커스텀 백엔드 ---

    def test_custom_backend(self):
        """커스텀 VisionModelBackend를 주입할 수 있어야 한다."""

        class CustomBackend(VisionModelBackend):
            def analyze_image(self, image_path: str) -> StructuredCaption:
                return StructuredCaption(color="빨간색", size="대형", details="천 재질")

        service = CaptionService(backend=CustomBackend())
        caption = service.generate_caption("/tmp/test.png")
        assert caption.color == "빨간색"
        assert caption.size == "대형"
        assert caption.details == "천 재질"

    def test_stub_backend_returns_placeholder(self):
        backend = StubVisionBackend()
        caption = backend.analyze_image("/tmp/test.png")
        assert caption.color != ""
        assert caption.size != ""
        assert caption.details != ""
