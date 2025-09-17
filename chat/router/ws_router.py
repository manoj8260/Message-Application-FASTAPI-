import logging
from fastapi import APIRouter ,  WebSocket ,WebSocketDisconnect ,Query
from servises.websocket_manager import WebSocketManager
from models.message import ChatMessage,MessageType
from datetime import datetime


logger = logging.getLogger(__name__)

ws_router = APIRouter()
manager = WebSocketManager()


@ws_router.websocket("/{username}")
async def websocket_endpoint(websocket: WebSocket ,username : str ,room_id : str  = Query(default='general')):
    """
    WebSocket endpoint for chat communication.
    
    Args:
        websocket: The WebSocket connection
        username: The username for the connection
        room_id: The room to join (default: "general")
    """
    await manager.connect(websocket,username,room_id)
    try : 
        while True :
            data =await websocket.receive_json()
            logger.info(f"Received message from {username}: {data}")
            # Create ChatMessage object
            chat_message = ChatMessage(
                username=username,
                message=data.get('message', ''),
                message_type=MessageType.CHAT,
                room_id=room_id,
                timestamp=datetime.utcnow()
            )
            # Broadcast message to room
            await manager.broadcast_to_room(room_id,chat_message.dict())
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {username}")
        await manager.disconnect(username)
    except Exception as e:
        logger.error(f"WebSocket error for user {username}: {str(e)}")
        await manager.disconnect(username)  
        

