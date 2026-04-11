"""채팅 비즈니스 로직 서비스"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatRoom
from app.schemas.chat import ChatRoomCreate


def create_chat_room(db: Session, data: ChatRoomCreate) -> ChatRoom:
    """채팅방을 생성한다.

    같은 분실물에 대해 동일한 습득자-분실자 조합의 채팅방이
    이미 존재하면 기존 채팅방을 반환한다.
    """
    existing = (
        db.query(ChatRoom)
        .filter(
            ChatRoom.lost_item_id == data.lost_item_id,
            ChatRoom.finder_id == data.finder_id,
            ChatRoom.seeker_id == data.seeker_id,
        )
        .first()
    )
    if existing:
        return existing

    room = ChatRoom(
        lost_item_id=data.lost_item_id,
        finder_id=data.finder_id,
        seeker_id=data.seeker_id,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def get_user_rooms(db: Session, user_id: int) -> list[ChatRoom]:
    """특정 사용자가 참여 중인 채팅방 목록을 조회한다."""
    return (
        db.query(ChatRoom)
        .filter((ChatRoom.finder_id == user_id) | (ChatRoom.seeker_id == user_id))
        .order_by(ChatRoom.created_at.desc())
        .all()
    )


def get_room_by_id(db: Session, room_id: int) -> ChatRoom:
    """채팅방 ID로 채팅방을 조회한다."""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채팅방을 찾을 수 없습니다.",
        )
    return room


def save_message(db: Session, room_id: int, sender_id: int, content: str, message_type: str = "text") -> ChatMessage:
    """메시지를 DB에 저장한다."""
    message = ChatMessage(room_id=room_id, sender_id=sender_id, content=content, message_type=message_type)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, room_id: int, limit: int = 50, offset: int = 0) -> list[ChatMessage]:
    """채팅방의 메시지 목록을 조회한다."""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.room_id == room_id)
        .order_by(ChatMessage.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def complete_chat(db: Session, room_id: int) -> ChatRoom:
    """채팅방 상태를 '찾기완료(completed)'로 변경한다."""
    room = get_room_by_id(db, room_id)
    room.status = "completed"
    db.commit()
    db.refresh(room)
    return room


def mark_messages_read(db: Session, room_id: int, reader_id: int) -> list[int]:
    """특정 사용자가 읽지 않은 상대방 메시지를 읽음 처리한다.

    Returns:
        읽음 처리된 메시지 ID 목록
    """
    unread = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.room_id == room_id,
            ChatMessage.sender_id != reader_id,
            ChatMessage.is_read == False,  # noqa: E712
        )
        .all()
    )
    read_ids = []
    for msg in unread:
        msg.is_read = True
        read_ids.append(msg.id)
    if read_ids:
        db.commit()
    return read_ids
