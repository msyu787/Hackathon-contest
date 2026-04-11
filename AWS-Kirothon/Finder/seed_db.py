"""DB 시딩 스크립트 - 분실물 샘플 데이터"""
from datetime import datetime
from app.core.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.lost_item import LostItem
from app.models.chat import ChatRoom, ChatMessage  # noqa: F401

# 기존 테이블 삭제 후 재생성
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 사용자 생성
u1 = User(id=1, name="김습득", student_id="20231001", birth_date="2000-03-15")
u2 = User(id=2, name="유민선", student_id="12345678", birth_date="2004-12-06")
db.add(u1)
db.add(u2)
db.flush()

# 분실물 4건 등록
items = [
    LostItem(
        id=1, finder_id=1, category="지갑", location="1공학관",
        found_at=datetime(2025, 3, 22, 18, 20),
        image_path="/static/uploads/wallet.jpeg",
        caption_color="검은색", caption_text="지갑",
        caption_details="카드가 약 5개 꼽혀있음",
        owner_name="유민선", status="active",
    ),
    LostItem(
        id=2, finder_id=1, category="텀블러", location="신소재공학관",
        found_at=datetime(2025, 3, 22, 13, 10),
        image_path="/static/uploads/tumbler.png",
        caption_color="흰색", caption_text="텀블러",
        caption_details="글씨가 적혀있지 않은 흰색 텀블러",
        status="active",
    ),
    LostItem(
        id=3, finder_id=2, category="우산", location="한플",
        found_at=datetime(2025, 3, 22, 15, 22),
        image_path="/static/uploads/umbrella.jpeg",
        caption_color="검은색", caption_text="우산",
        caption_details="체크무늬, 고리 있음, 자동식 우산",
        status="active",
    ),
]

for item in items:
    db.add(item)

db.commit()
db.close()
print("DB 시딩 완료! 3개 분실물 등록됨")
