import logging
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from typing import Dict, List
from models.message import ChatMessage, MessageType
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and handles message broadcasting.

    This class maintains active connections, handles user join/leave events,
    and broadcasts messages to connected clients.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, str] = {}   # username -> room_id
        self.room_users: Dict[str, List[str]] = {}  # room_id -> [usernames]

    async def connect(self, websocket: WebSocket, username: str, room_id: str = "general"):
        """Accept a new WebSocket connection and add user to room."""
        await websocket.accept()

        # Track connection
        self.active_connections[username] = websocket
        self.user_rooms[username] = room_id

        if room_id not in self.room_users:
            self.room_users[room_id] = []
        if username not in self.room_users[room_id]:
            self.room_users[room_id].append(username)

        # Notify room about user join
        join_message = ChatMessage(
            username=username,
            message=f"{username} joined the room",
            message_type=MessageType.USER_JOIN,
            room_id=room_id,
            timestamp=datetime.utcnow(),
        )
        await self.broadcast_to_room(room_id, join_message)

        logger.info(f"User {username} connected to room {room_id}")
        logger.info(f"Active connections: {list(self.active_connections.keys())}")

    async def disconnect(self, username: str):
        """Remove a user's WebSocket connection."""
        if username in self.active_connections:
            room_id = self.user_rooms.get(username, "general")

            # Remove from room
            await self._leave_room(username)

            leave_message = ChatMessage(
                username=username,
                message=f"{username} left the room",
                message_type=MessageType.USER_LEAVE,
                room_id=room_id,
                timestamp=datetime.utcnow(),
            )
            await self.broadcast_to_room(room_id, leave_message)

            logger.info(f"User {username} disconnected from room {room_id}")

    async def _leave_room(self, username: str):
        """Remove user from their current room."""
        if username in self.user_rooms:
            old_room = self.user_rooms[username]
            if old_room in self.room_users and username in self.room_users[old_room]:
                self.room_users[old_room].remove(username)

                # Clean up empty rooms
                if not self.room_users[old_room]:
                    del self.room_users[old_room]

            del self.user_rooms[username]

        if username in self.active_connections:
            del self.active_connections[username]

    async def send_personal_message(self, username: str, message):
        """
        Send a message to a specific user.
        `message` can be a dict or a Pydantic model.
        """
        if username in self.active_connections:
            websocket = self.active_connections[username]
            try:
                await websocket.send_json(jsonable_encoder(message))
                logger.info(f"Message sent to {username}")
            except Exception as e:
                logger.error(f"Error sending message to {username}: {str(e)}")
                await self.disconnect(username)

    async def broadcast_to_room(self, room_id: str, message):
        """
        Broadcast a message to all users in a room.
        `message` can be a dict or a Pydantic model.
        """
        if room_id in self.room_users:
            disconnected_users = []
            for username in self.room_users[room_id]:
                if username in self.active_connections:
                    try:
                        await self.active_connections[username].send_json(jsonable_encoder(message))
                    except Exception as e:
                        logger.error(f"Error sending message to {username}: {str(e)}")
                        disconnected_users.append(username)

            # Clean up disconnected users
            for username in disconnected_users:
                await self.disconnect(username)

    async def get_room_users(self, room_id: str) -> List[str]:
        """Return the list of users in a room."""
        return self.room_users.get(room_id, [])
     
    async def get_user_room(self, username: str) -> str:
        """
        Get the room a user is currently in.

        """
        return self.user_rooms.get(username, "general")

    def get_all_rooms(self) -> List[str]:
        """
        Get list of all active rooms.
        """
        return list(self.room_users.keys())