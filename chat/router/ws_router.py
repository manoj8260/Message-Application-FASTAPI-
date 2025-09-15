import logging
from fastapi import APIRouter ,  WebSocket ,WebSocketDisconnect ,Query
from servises.websocket_manager import WebSocketManager
from models.message import ChatMessage,MessageType
from datetime import datetime


logger = logging.getLogger(__name__)

router = APIRouter()
manager = WebSocketManager()


@router.websocket("/ws/{username}")
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
        

@router.get('/rooms')
async def get_rooms():
    """
    Get list of all active rooms.
    
    Returns:
        List of active room names
    """
    return {"rooms": manager.get_all_rooms()}


@router.get('/rooms/{room_id}/users')
async def get_room_users(room_id: str):
    """
    Get list of users in a specific room.
    
    Args:
        room_id: The room ID
        
    Returns:
        List of users in the room
    """
    users = await manager.get_room_users(room_id)
    return {"room_id": room_id, "users": users}              
    