"""LostItem 모델 및 스키마 단위 테스트"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models.lost_item import CategoryEnum, LostItem, StatusEnum
from app.models.user import User
from app.schemas.lost_item import CaptionUpdate, LostItemCreate, LostItemResponse


@pytest.fixture
def db_session():
    """테스트용 인메모리 SQLite DB"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """테스트용 사용자 생성"""
    user = User(name="테스트유저")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestCategoryEnum:
    """CategoryEnum 유효성 테스트"""

    def test_valid_categories(self):
        """유효한 카테고리 값 확인"""
        assert CategoryEnum.지갑.value == "지갑"
        assert CategoryEnum.카드.value == "카드"
        assert CategoryEnum.신분증.value == "신분증"
        assert CategoryEnum.전자기기.value == "전자기기"
        assert CategoryEnum.기타.value == "기타"

    def test_category_count(self):
        """카테고리가 정확히 5개인지 확인"""
        assert len(CategoryEnum) == 5

    def test_invalid_category_rejected(self):
        """유효하지 않은 카테고리 거부"""
        with pytest.raises(ValueError):
            CategoryEnum("가방")


class TestStatusEnum:
    """StatusEnum 유효성 테스트"""

    def test_valid_statuses(self):
        """유효한 상태 값 확인"""
        assert StatusEnum.active.value == "active"
        assert StatusEnum.pending.value == "pending"
        assert StatusEnum.completed.value == "completed"


class TestLostItemModel:
    """LostItem SQLAlchemy 모델 테스트"""

    def test_create_lost_item(self, db_session: Session, sample_user: User):
        """LostItem 레코드 생성 및 조회"""
        item = LostItem(
            finder_id=sample_user.id,
            category=CategoryEnum.지갑.value,
            location="서울역 1번 출구",
            found_at=datetime(2024, 1, 15, 10, 30, tzinfo=UTC),
            image_path="/uploads/wallet.jpg",
        )
        db_session.add(item)
        db_session.commit()

        saved = db_session.query(LostItem).first()
        assert saved is not None
        assert saved.finder_id == sample_user.id
        assert saved.category == "지갑"
        assert saved.location == "서울역 1번 출구"
        assert saved.image_path == "/uploads/wallet.jpg"
        assert saved.status == "active"
        assert isinstance(saved.created_at, datetime)

    def test_table_columns(self, db_session: Session):
        """테이블 컬럼 구조 검증"""
        inspector = inspect(db_session.bind)
        columns = {col["name"] for col in inspector.get_columns("lost_items")}
        expected = {
            "id", "finder_id", "category", "location", "found_at",
            "image_path", "caption_color", "caption_size", "caption_details",
            "caption_text", "caption_embedding", "owner_name", "status",
            "created_at",
        }
        assert expected == columns

    def test_nullable_caption_fields(self, db_session: Session, sample_user: User):
        """캡션 필드가 nullable인지 확인"""
        item = LostItem(
            finder_id=sample_user.id,
            category=CategoryEnum.카드.value,
            location="강남역",
            found_at=datetime(2024, 1, 15, tzinfo=UTC),
            image_path="/uploads/card.jpg",
        )
        db_session.add(item)
        db_session.commit()

        saved = db_session.query(LostItem).first()
        assert saved.caption_color is None
        assert saved.caption_size is None
        assert saved.caption_details is None
        assert saved.caption_text is None
        assert saved.caption_embedding is None
        assert saved.owner_name is None

    def test_default_status_active(self, db_session: Session, sample_user: User):
        """기본 상태가 active인지 확인"""
        item = LostItem(
            finder_id=sample_user.id,
            category=CategoryEnum.기타.value,
            location="도서관",
            found_at=datetime(2024, 1, 15, tzinfo=UTC),
            image_path="/uploads/other.jpg",
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        assert item.status == "active"

    def test_foreign_key_constraint(self, db_session: Session):
        """finder_id FK 제약조건 검증"""
        inspector = inspect(db_session.bind)
        fks = inspector.get_foreign_keys("lost_items")
        fk_columns = [fk["constrained_columns"] for fk in fks]
        assert ["finder_id"] in fk_columns


class TestLostItemSchemas:
    """LostItem Pydantic 스키마 테스트"""

    def test_lost_item_create_valid(self):
        """LostItemCreate 유효한 입력"""
        schema = LostItemCreate(
            category=CategoryEnum.지갑,
            location="서울역",
            found_at=datetime(2024, 1, 15, 10, 30),
        )
        assert schema.category == CategoryEnum.지갑
        assert schema.location == "서울역"

    def test_lost_item_create_invalid_category(self):
        """LostItemCreate 유효하지 않은 카테고리 거부"""
        with pytest.raises(ValidationError):
            LostItemCreate(
                category="가방",
                location="서울역",
                found_at=datetime(2024, 1, 15),
            )

    def test_lost_item_create_empty_location_rejected(self):
        """LostItemCreate 빈 장소 거부"""
        with pytest.raises(ValidationError):
            LostItemCreate(
                category=CategoryEnum.지갑,
                location="",
                found_at=datetime(2024, 1, 15),
            )

    def test_lost_item_response_from_attributes(
        self, db_session: Session, sample_user: User
    ):
        """LostItemResponse가 ORM 객체에서 변환되는지 확인"""
        item = LostItem(
            finder_id=sample_user.id,
            category=CategoryEnum.전자기기.value,
            location="카페",
            found_at=datetime(2024, 1, 15, tzinfo=UTC),
            image_path="/uploads/phone.jpg",
            caption_color="검정색",
            caption_size="손바닥 크기",
            caption_details="삼성 갤럭시",
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        response = LostItemResponse.model_validate(item)
        assert response.id == item.id
        assert response.category == "전자기기"
        assert response.caption_color == "검정색"
        assert response.status == "active"

    def test_caption_update_valid(self):
        """CaptionUpdate 유효한 입력"""
        schema = CaptionUpdate(
            color="검정색",
            size="손바닥 크기",
            details="가죽 재질, 지퍼 있음",
        )
        assert schema.color == "검정색"
        assert schema.size == "손바닥 크기"
        assert schema.details == "가죽 재질, 지퍼 있음"

    def test_caption_update_empty_fields_rejected(self):
        """CaptionUpdate 빈 필드 거부"""
        with pytest.raises(ValidationError):
            CaptionUpdate(color="", size="크기", details="세부")
