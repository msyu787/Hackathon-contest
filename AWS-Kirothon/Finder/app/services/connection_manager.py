"""WebSocket 연결 관리 모듈"""

from fastapi import WebSocket


class ConnectionManager:
    """채팅방별 WebSocket 연결을 관리하는 클래스."""

    def __init__(self) -> None:
        # {room_id: [WebSocket, ...]}
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int) -> None:
        """WebSocket 연결을 수락하고 채팅방에 추가한다."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int) -> None:
        """WebSocket 연결을 채팅방에서 제거한다."""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, room_id: int, message: dict) -> None:
        """채팅방의 모든 연결에 메시지를 브로드캐스트한다."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()
