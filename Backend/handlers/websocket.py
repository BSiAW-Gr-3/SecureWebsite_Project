"""
WebSocket connection manager for real-time chat
"""
from fastapi import WebSocket
from typing import List, Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat: str):
        """Accept and store a connection within a specific room"""
        await websocket.accept()
        if chat not in self.active_connections:
            self.active_connections[chat] = []
        self.active_connections[chat].append(websocket)

    def disconnect(self, websocket: WebSocket, chat: str):
        """Remove a connection from a specific room"""
        if chat in self.active_connections:
            self.active_connections[chat].remove(websocket)
            if not self.active_connections[chat]:
                del self.active_connections[chat]

    async def broadcast(self, message: dict, chat: str):
        """Send a message only to participants of a specific room"""
        if chat in self.active_connections:
            for connection in self.active_connections[chat]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()