"""분실물 등록 서비스 — 사진 업로드, 캡션 생성, DB 저장 파이프라인"""

import os
import uuid
from datetime import UTC, datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import CaptionFailedException, UploadFailedException
from app.models.lost_item import LostItem
from app.services.caption_service import CaptionService

UPLOAD_DIR = "uploads"


class ItemService:
    """분실물 등록 서비스.

    사진 업로드 → 캡션 생성 → DB 저장 파이프라인을 처리한다.
    캡션 생성 실패 시 pending 상태로 저장하여 수동 캡션 입력을 유도한다.
    """

    def __init__(self, caption_service: CaptionService | None = None) -> None:
        self._caption_service = caption_service or CaptionService()

    async def _save_upload(self, image_file: UploadFile) -> str:
        """업로드된 파일을 로컬 저장소에 저장한다.

        Args:
            image_file: FastAPI UploadFile 객체.

        Returns:
            저장된 파일의 상대 경로.

        Raises:
            UploadFailedException: 파일 저장 실패 시.
        """
        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            ext = ""
            if image_file.filename:
                ext = os.path.splitext(image_file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            content = await image_file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            return file_path
        except Exception as e:
            raise UploadFailedException() from e

    def create_item(
        self,
        db: Session,
        finder_id: int,
        category: str,
        location: str,
        found_at: datetime,
        image_path: str,
    ) -> LostItem:
        """분실물을 등록한다.

        캡션 생성 성공 시 active, 실패 시 pending 상태로 저장한다.
        임베딩 벡터는 매칭 서비스(Task 6.1)에서 처리하므로 None으로 저장한다.

        Args:
            db: SQLAlchemy 세션.
            finder_id: 발견자 ID.
            category: 카테고리 문자열.
            location: 발견 장소.
            found_at: 발견 시간.
            image_path: 저장된 이미지 파일 경로.

        Returns:
            생성된 LostItem 객체.
        """
        caption_color = None
        caption_size = None
        caption_details = None
        caption_text = None
        status = "active"

        try:
            caption = self._caption_service.generate_caption(image_path)
            caption_color = caption.color
            caption_size = caption.size
            caption_details = caption.details
            caption_text = self._caption_service.caption_to_text(caption)
        except CaptionFailedException:
            status = "pending"

        item = LostItem(
            finder_id=finder_id,
            category=category,
            location=location,
            found_at=found_at,
            image_path=image_path,
            caption_color=caption_color,
            caption_size=caption_size,
            caption_details=caption_details,
            caption_text=caption_text,
            caption_embedding=None,
            status=status,
            created_at=datetime.now(UTC),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
