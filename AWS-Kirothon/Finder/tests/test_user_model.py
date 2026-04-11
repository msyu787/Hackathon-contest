"""User 모델 및 스키마 단위 테스트"""

from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


# 테스트용 인메모리 SQLite DB
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


class TestUserModel:
    """User SQLAlchemy 모델 테스트"""

    def test_create_user(self, db_session: Session):
        """User 레코드 생성 및 조회"""
        user = User(name="홍길동")
        db_session.add(user)
        db_session.commit()

        saved = db_session.query(User).first()
        assert saved is not None
        assert saved.name == "홍길동"
        assert isinstance(saved.created_at, datetime)
        assert saved.id is not None

    def test_table_columns(self, db_session: Session):
        """테이블 컬럼 구조 검증"""
        inspector = inspect(db_session.bind)
        columns = {col["name"] for col in inspector.get_columns("users")}
        expected = {"id", "name", "created_at"}
        assert expected == columns

    def test_name_not_null(self, db_session: Session):
        """name 필드 NOT NULL 제약조건 검증"""
        from sqlalchemy.exc import IntegrityError

        user = User(name=None)
        db_session.add(user)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUserSchemas:
    """User Pydantic 스키마 테스트"""

    def test_user_create_valid(self):
        """UserCreate 유효한 입력"""
        schema = UserCreate(name="홍길동")
        assert schema.name == "홍길동"

    def test_user_create_empty_name_rejected(self):
        """UserCreate 빈 이름 거부"""
        with pytest.raises(ValidationError):
            UserCreate(name="")

    def test_user_response_from_attributes(self, db_session: Session):
        """UserResponse가 ORM 객체에서 변환되는지 확인"""
        user = User(name="홍길동")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        response = UserResponse.model_validate(user)
        assert response.id == user.id
        assert response.name == "홍길동"
        assert isinstance(response.created_at, datetime)
