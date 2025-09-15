from fastapi import APIRouter
from  servises.websocket_manager   import WebSocketManager

api_router  = APIRouter()
manager = WebSocketManager()


@api_router.get('/rooms')
async def get_rooms():
    """
    Get list of all active rooms.
    
    Returns:
        List of active room names
    """
    return {"rooms": manager.get_all_rooms()}


@api_router.get('/rooms/{room_id}/users')
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
    