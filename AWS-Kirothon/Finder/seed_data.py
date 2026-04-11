"""테스트 데이터 입력 스크립트"""
import shutil
import os
from datetime import datetime

from app.core.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.lost_item import LostItem
from app.models.chat import ChatRoom, ChatMessage  # noqa: F401

Base.metadata.create_all(bind=engine)

# 이미지 복사
os.makedirs("static/uploads", exist_ok=True)

image_files = ["wallet.jpeg", "tumbler.jpeg", "umbrella.jpeg"]
for fname in image_files:
    src = os.path.join(r"C:\Users\msyu7\Desktop", fname)
    dst = os.path.join("static/uploads", fname)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"이미지 복사 완료: {dst}")

db = SessionLocal()

# 사용자 데이터
u1 = User(id=1, name="김습득", student_id="20231001", birth_date="2000-03-15")
u2 = User(id=2, name="유민선", student_id="12345678", birth_date="2004-12-06")
db.merge(u1)
db.merge(u2)

# 분실물 데이터
items = [
    LostItem(
        id=1,
        finder_id=1,
        category="지갑",
        location="1공학관",
        found_at=datetime(2025, 3, 22, 18, 20),
        image_path="/static/uploads/wallet.jpeg",
        caption_color="검은색",
        caption_text="검은색 지갑",
        owner_name="유민선",
        status="active",
    ),
    LostItem(
        id=2,
        finder_id=1,
        category="기타",
        location="신소재공학관",
        found_at=datetime(2025, 3, 22, 13, 10),
        image_path="/static/uploads/tumbler.jpeg",
        caption_color="흰색",
        caption_text="흰색 텀블러",
        status="active",
    ),
    LostItem(
        id=3,
        finder_id=2,
        category="기타",
        location="한플",
        found_at=datetime(2025, 3, 22, 15, 22),
        image_path="/static/uploads/umbrella.jpeg",
        caption_color="검은색",
        caption_text="검은색 우산",
        status="active",
    ),
]

for item in items:
    db.merge(item)

db.commit()
db.close()
print("테스트 데이터 입력 완료!")
