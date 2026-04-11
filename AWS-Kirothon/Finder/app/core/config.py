"""애플리케이션 환경 설정 관리 모듈"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic Settings를 활용한 환경 설정 클래스.

    환경변수 또는 .env 파일에서 설정값을 로드한다.
    SQLite(개발) / PostgreSQL(운영) 전환은 DATABASE_URL 환경변수로 제어한다.
    """

    DATABASE_URL: str = "sqlite:///./finder.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    APP_NAME: str = "분실물 찾아주기 AI 매칭 플랫폼"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
