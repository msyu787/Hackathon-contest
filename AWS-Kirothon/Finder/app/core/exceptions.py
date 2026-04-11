"""커스텀 예외 클래스 및 FastAPI 예외 핸들러 등록"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """애플리케이션 공통 예외 클래스.

    Attributes:
        status_code: HTTP 상태 코드
        error_code: 오류 유형 코드 문자열
        message: 한국어 오류 메시지
    """

    def __init__(self, status_code: int, error_code: str, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(message)


# --- 구체적 예외 클래스 ---


class ValidationException(AppException):
    """입력값 유효성 검증 실패"""

    def __init__(self, message: str = "입력값이 유효하지 않습니다") -> None:
        super().__init__(status_code=400, error_code="VALIDATION_ERROR", message=message)


class UnsupportedFormatException(AppException):
    """지원하지 않는 이미지 형식"""

    def __init__(
        self, message: str = "지원하지 않는 이미지 형식입니다. 지원 형식: jpg, jpeg, png, webp"
    ) -> None:
        super().__init__(status_code=400, error_code="UNSUPPORTED_FORMAT", message=message)


class UploadFailedException(AppException):
    """파일 업로드 실패"""

    def __init__(self, message: str = "사진 업로드에 실패했습니다. 다시 시도해주세요") -> None:
        super().__init__(status_code=500, error_code="UPLOAD_FAILED", message=message)


class CaptionFailedException(AppException):
    """AI 캡션 생성 실패"""

    def __init__(
        self, message: str = "자동 캡션 생성에 실패했습니다. 수동으로 입력해주세요"
    ) -> None:
        super().__init__(status_code=500, error_code="CAPTION_FAILED", message=message)


class AuthRequiredException(AppException):
    """인증 토큰 없음/만료"""

    def __init__(self, message: str = "로그인이 필요합니다") -> None:
        super().__init__(status_code=401, error_code="AUTH_REQUIRED", message=message)


class DuplicatePhoneException(AppException):
    """전화번호 중복 가입"""

    def __init__(self, message: str = "이미 등록된 전화번호입니다") -> None:
        super().__init__(status_code=409, error_code="DUPLICATE_PHONE", message=message)


class VerificationFailedException(AppException):
    """인증 코드 불일치"""

    def __init__(self, message: str = "인증 코드가 일치하지 않습니다") -> None:
        super().__init__(
            status_code=400, error_code="VERIFICATION_FAILED", message=message
        )


class VerificationLockedException(AppException):
    """인증 시도 횟수 초과"""

    def __init__(
        self,
        message: str = "인증 시도 횟수를 초과했습니다. 30분 후 다시 시도해주세요",
    ) -> None:
        super().__init__(
            status_code=429, error_code="VERIFICATION_LOCKED", message=message
        )


class NameMismatchException(AppException):
    """이름 매칭 검증 실패"""

    def __init__(self, message: str = "본인 소유 분실물만 요청할 수 있습니다") -> None:
        super().__init__(status_code=403, error_code="NAME_MISMATCH", message=message)


class NotFoundException(AppException):
    """리소스 없음"""

    def __init__(self, message: str = "해당 게시물을 찾을 수 없습니다") -> None:
        super().__init__(status_code=404, error_code="NOT_FOUND", message=message)


def register_exception_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 예외 핸들러를 등록한다."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
                "error_code": exc.error_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "data": None,
                "message": "입력값이 유효하지 않습니다",
                "error_code": "VALIDATION_ERROR",
            },
        )
