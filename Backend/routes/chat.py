"""
Chat routes: message history and WebSocket real-time chat
"""
from handlers.auth import get_current_active_user
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from typing import List

from schemas.schemas import ChatMessageResponse
from schemas.models import ChatMessage, User
from handlers.websocket import manager
from handlers.database import get_db

from config import SECRET_KEY, ALGORITHM, CHAT_PREFIX

router = APIRouter()

@router.get("/api/chat/history/{chat}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    chat: str,
    limit: int = 50,
):
    """Get chat message history"""
    db = get_db()
    messages = await db.get_recent_messages(chat, limit)
    
    return [
        ChatMessageResponse(
            username=msg.username,
            message=msg.message,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]

@router.get("/api/chat/status/{chat}")
async def get_chat_status(chat: str, current_user: User = Depends(get_current_active_user)):
    """
    Check if a chat table is 'ACTIVE', 'CREATING', or 'NOT_FOUND'.
    """
    db = get_db()
    status = await db.check_table_status(chat)
    return {"status": status}

@router.get("/api/chat/list", response_model=List[str])
async def get_chat_list(current_user: User = Depends(get_current_active_user)):
    """Get list of available chats"""
    db = get_db()
    chats = await db.get_chat_tables()
    return chats

@router.post("/api/chat/create/{chat}")
async def create_chat(chat: str, current_user: User = Depends(get_current_active_user)):
    """Create a new chat table"""
    db = get_db()
    await db.create_chat_tables(chat)
    return {"message": f"Chat '{chat}' created successfully."}

@router.websocket("/api/ws/chat/{chat}")
async def websocket_chat(websocket: WebSocket, chat: str):
    """WebSocket endpoint for real-time chat"""
    db = get_db()
    await manager.connect(websocket, chat)

    chat_plain_name = chat.removeprefix(CHAT_PREFIX)
    
    try:
        token = await websocket.receive_text()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                await websocket.close(code=1008)
                return
            
            user = await db.get_user_by_username(username)
            if user is None or not user.is_active:
                await websocket.close(code=1008)
                return
        except JWTError:
            await websocket.close(code=1008)
            return
        
        await websocket.send_json({
            "type": "system",
            "message": f"Welcome {username}! You are now connected to the chat."
        })
        
        recent_messages = await db.get_recent_messages(chat_plain_name, 50)
        
        if recent_messages:
            await websocket.send_json({
                "type": "history",
                "messages": [
                    {
                        "username": msg.username,
                        "message": msg.message,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in recent_messages
                ]
            })
        
        while True:
            data = await websocket.receive_text()
            
            if data.startswith("/"):
                command_parts = data.split(maxsplit=1)
                command = command_parts[0].lower()
                
                if command == "/history":
                    limit = 50
                    if len(command_parts) > 1 and command_parts[1].isdigit():
                        limit = int(command_parts[1])
                        limit = min(limit, 200) 
                    
                    history_messages = await db.get_recent_messages(chat_plain_name, limit)
                    
                    await websocket.send_json({
                        "type": "history",
                        "messages": [
                            {
                                "username": msg.username,
                                "message": msg.message,
                                "timestamp": msg.timestamp.isoformat()
                            }
                            for msg in history_messages
                        ]
                    })
                    continue
                
                elif command == "/help":
                    await websocket.send_json({
                        "type": "system",
                        "message": "Available commands:\n/history [number] - Get recent messages (default 50, max 200)\n/help - Show this help message"
                    })
                    continue
            
            chat_message = ChatMessage(username=username, message=data)
            await db.create_message(chat_message, chat_plain_name)
            
            message_data = {
                "type": "message",
                "username": username,
                "message": data,
                "timestamp": chat_message.timestamp.isoformat()
            }
            await manager.broadcast(message_data, chat)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat)
    except Exception as e:
        manager.disconnect(websocket, chat)
        print(f"WebSocket error: {e}")