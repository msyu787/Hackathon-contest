"""데이터베이스 연결 및 SQLAlchemy 설정 모듈"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# SQLite 사용 시 check_same_thread=False 필요
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 선언적 베이스 클래스"""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 DB 세션 제너레이터.

    요청마다 새 세션을 생성하고, 요청 완료 후 자동으로 닫는다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
