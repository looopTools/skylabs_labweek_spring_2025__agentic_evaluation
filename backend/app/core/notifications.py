import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import WebSocket

# Configure logging
logger = logging.getLogger(__name__)

class Notification(BaseModel):
    """Notification model"""
    id: str
    type: str
    message: str
    created_at: datetime
    data: Optional[Dict[str, Any]] = None
    read: bool = False

class NotificationManager:
    """Notification manager for WebSocket connections"""
    def __init__(self):
        self._connections: Dict[str, WebSocket] = {}
        self._notifications: Dict[str, List[Notification]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """Connect a new client"""
        await websocket.accept()
        self._connections[client_id] = websocket
        if client_id not in self._notifications:
            self._notifications[client_id] = []

    def disconnect(self, client_id: str):
        """Disconnect a client"""
        self._connections.pop(client_id, None)

    async def send_notification(
        self,
        client_id: str,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send a notification to a client"""
        try:
            notification = Notification(
                id=f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                type=notification_type,
                message=message,
                created_at=datetime.now(),
                data=data
            )

            # Store notification
            if client_id in self._notifications:
                self._notifications[client_id].append(notification)

            # Send to connected client
            if client_id in self._connections:
                websocket = self._connections[client_id]
                try:
                    await websocket.send_json(notification.dict())
                except Exception as e:
                    logger.error(f"Failed to send notification: {e}")
                    self.disconnect(client_id)

        except Exception as e:
            logger.error(f"Error in send_notification: {e}", exc_info=True)

    async def broadcast(
        self,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Broadcast a notification to all connected clients"""
        disconnected = []
        for client_id in self._connections:
            try:
                await self.send_notification(client_id, notification_type, message, data)
            except Exception:
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    def get_notifications(
        self,
        client_id: str,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a client"""
        notifications = self._notifications.get(client_id, [])
        if unread_only:
            return [n for n in notifications if not n.read]
        return notifications

    def mark_as_read(self, client_id: str, notification_id: str):
        """Mark a notification as read"""
        notifications = self._notifications.get(client_id, [])
        for notification in notifications:
            if notification.id == notification_id:
                notification.read = True
                break

    def cleanup_old_notifications(self, max_age_days: int = 30):
        """Clean up old notifications"""
        now = datetime.now()
        for client_id in self._notifications:
            self._notifications[client_id] = [
                n for n in self._notifications[client_id]
                if (now - n.created_at).days <= max_age_days
            ]

# Global notification manager instance
notification_manager = NotificationManager()

def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    return notification_manager