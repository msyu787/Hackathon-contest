"""채팅 API 라우터 (REST + WebSocket)"""

import json
import os
import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lost_item import LostItem
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRoomCreate,
    ChatRoomResponse,
    VerifyRequest,
)
from app.services.chat_service import (
    complete_chat,
    create_chat_room,
    get_messages,
    get_room_by_id,
    get_user_rooms,
    mark_messages_read,
    save_message,
)
from app.services.connection_manager import manager

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/rooms", response_model=ChatRoomResponse)
def create_room(data: ChatRoomCreate, db: Session = Depends(get_db)):
    """채팅방을 생성한다."""
    return create_chat_room(db, data)


@router.get("/rooms", response_model=list[ChatRoomResponse])
def list_rooms(user_id: int = Query(..., description="사용자 ID"), db: Session = Depends(get_db)):
    """사용자가 참여 중인 채팅방 목록을 조회한다."""
    return get_user_rooms(db, user_id)


@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """채팅방 상세 정보를 조회한다."""
    return get_room_by_id(db, room_id)


VERIFICATION_CATEGORIES = {"지갑", "핸드폰"}


@router.get("/rooms/{room_id}/info")
def get_room_info(room_id: int, db: Session = Depends(get_db)):
    """채팅방 상세 정보 + 분실물 정보를 조회한다."""
    room = get_room_by_id(db, room_id)
    item = db.query(LostItem).filter(LostItem.id == room.lost_item_id).first()
    item_name = item.category if item else "분실물"
    requires_verification = item.category in VERIFICATION_CATEGORIES if item else False
    return {
        "room_id": room.id,
        "finder_id": room.finder_id,
        "seeker_id": room.seeker_id,
        "status": room.status,
        "item_name": item_name,
        "item_location": item.location if item else "",
        "item_image": item.image_path if item else "",
        "requires_verification": requires_verification,
    }


@router.post("/rooms/{room_id}/verify")
def verify_identity(
    room_id: int,
    body: VerifyRequest,
    db: Session = Depends(get_db),
):
    """본인인증: 입력한 이름과 분실물 소유자 이름을 비교한다."""
    room = get_room_by_id(db, room_id)
    item = db.query(LostItem).filter(LostItem.id == room.lost_item_id).first()

    if not item:
        return {"verified": False, "message": "분실물 정보를 찾을 수 없습니다."}

    if item.category not in VERIFICATION_CATEGORIES:
        return {"verified": False, "message": "본인인증이 필요하지 않은 물품입니다."}

    if not item.owner_name:
        return {"verified": False, "message": "습득자가 소유자 이름을 등록하지 않았습니다."}

    if body.name.strip() == item.owner_name.strip():
        return {"verified": True, "message": f"✅ 본인인증 성공! {body.name}님 확인되었습니다."}
    else:
        return {"verified": False, "message": "❌ 본인인증 실패. 이름이 일치하지 않습니다."}


@router.post("/rooms/{room_id}/upload")
async def upload_image(
    room_id: int,
    sender_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """채팅에서 이미지를 업로드한다."""
    get_room_by_id(db, room_id)
    ext = os.path.splitext(file.filename or "img.png")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    image_url = f"/static/uploads/{filename}"
    msg = save_message(db, room_id, sender_id, image_url, message_type="image")
    return {"id": msg.id, "image_url": image_url, "created_at": msg.created_at.isoformat()}


@router.get("/rooms/{room_id}/messages", response_model=list[ChatMessageResponse])
def list_messages(
    room_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """채팅방의 메시지 목록을 조회한다."""
    return get_messages(db, room_id, limit=limit, offset=offset)


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
def send_message(
    room_id: int,
    data: ChatMessageCreate,
    sender_id: int = Query(..., description="발신자 ID"),
    db: Session = Depends(get_db),
):
    """REST로 메시지를 전송한다 (WebSocket 미사용 시 폴백)."""
    # 채팅방 존재 여부 확인
    get_room_by_id(db, room_id)
    return save_message(db, room_id, sender_id, data.content)


@router.patch("/rooms/{room_id}/complete", response_model=ChatRoomResponse)
def mark_complete(room_id: int, db: Session = Depends(get_db)):
    """채팅방을 '찾기완료' 상태로 변경한다."""
    return complete_chat(db, room_id)


@router.websocket("/ws/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: int, sender_id: int = Query(...)):
    """WebSocket 실시간 채팅 엔드포인트.

    송신: {"type": "message", "content": "..."} 또는 {"type": "read"}
    수신: {"type": "message", ...} / {"type": "read", "message_ids": [...]} / {"type": "system", ...}
    """
    db: Session = next(get_db())
    try:
        get_room_by_id(db, room_id)
        await manager.connect(websocket, room_id)

        # 입장 시 상대방 메시지 읽음 처리
        read_ids = mark_messages_read(db, room_id, sender_id)
        if read_ids:
            await manager.broadcast(room_id, {
                "type": "read",
                "reader_id": sender_id,
                "message_ids": read_ids,
            })

        await manager.broadcast(room_id, {
            "type": "system",
            "content": f"사용자 {sender_id}님이 입장했습니다.",
        })

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg_type = data.get("type", "message")

            if msg_type == "read":
                # 읽음 처리 요청
                read_ids = mark_messages_read(db, room_id, sender_id)
                if read_ids:
                    await manager.broadcast(room_id, {
                        "type": "read",
                        "reader_id": sender_id,
                        "message_ids": read_ids,
                    })
            elif msg_type == "message":
                content = data.get("content", "")
                if not content:
                    continue
                msg = save_message(db, room_id, sender_id, content)
                await manager.broadcast(room_id, {
                    "type": "message",
                    "id": msg.id,
                    "sender_id": sender_id,
                    "content": content,
                    "message_type": "text",
                    "created_at": msg.created_at.isoformat(),
                    "is_read": False,
                })
            elif msg_type == "image":
                # 이미지 URL을 받아서 브로드캐스트 (업로드는 REST로 처리)
                image_url = data.get("image_url", "")
                msg_id = data.get("id", 0)
                created_at = data.get("created_at", "")
                await manager.broadcast(room_id, {
                    "type": "message",
                    "id": msg_id,
                    "sender_id": sender_id,
                    "content": image_url,
                    "message_type": "image",
                    "created_at": created_at,
                    "is_read": False,
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "system",
            "content": f"사용자 {sender_id}님이 퇴장했습니다.",
        })
    finally:
        db.close()
