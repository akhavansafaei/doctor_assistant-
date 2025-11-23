"""WebSocket connection manager for real-time chat"""
from typing import Dict, Set
from fastapi import WebSocket
from datetime import datetime
import json
import asyncio
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""

    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # User sessions: user_id -> Set[session_id]
        self.user_sessions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)

        logger.info(f"WebSocket connected: session={session_id}, user={user_id}")

        # Send connection confirmation
        await self.send_message(session_id, {
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    def disconnect(self, session_id: str, user_id: str = None):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if user_id and user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]

        logger.info(f"WebSocket disconnected: session={session_id}")

    async def send_message(self, session_id: str, message: dict):
        """Send a message to a specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)

    async def send_text(self, session_id: str, text: str):
        """Send plain text to a session"""
        await self.send_message(session_id, {"type": "text", "content": text})

    async def stream_token(self, session_id: str, token: str):
        """Stream a single token to the client"""
        await self.send_message(session_id, {
            "type": "token",
            "content": token,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def stream_start(self, session_id: str, metadata: dict = None):
        """Signal start of streaming"""
        message = {
            "type": "stream_start",
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        await self.send_message(session_id, message)

    async def stream_end(self, session_id: str, metadata: dict = None):
        """Signal end of streaming"""
        message = {
            "type": "stream_end",
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        await self.send_message(session_id, message)

    async def send_error(self, session_id: str, error: str, error_type: str = "general"):
        """Send error message to client"""
        await self.send_message(session_id, {
            "type": "error",
            "error_type": error_type,
            "message": error,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def send_status(self, session_id: str, status: str, details: dict = None):
        """Send status update to client"""
        message = {
            "type": "status",
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        if details:
            message["details"] = details
        await self.send_message(session_id, message)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all sessions of a user"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                await self.send_message(session_id, message)

    def get_active_sessions(self, user_id: str = None) -> Set[str]:
        """Get all active sessions, optionally filtered by user"""
        if user_id:
            return self.user_sessions.get(user_id, set())
        return set(self.active_connections.keys())

    def is_connected(self, session_id: str) -> bool:
        """Check if a session is connected"""
        return session_id in self.active_connections


# Global connection manager instance
connection_manager = ConnectionManager()
