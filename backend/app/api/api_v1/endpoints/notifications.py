from typing import List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from app.core.notifications import (
    get_notification_manager,
    NotificationManager,
    Notification
)

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    notification_manager: NotificationManager = Depends(get_notification_manager)
):
    """WebSocket endpoint for real-time notifications"""
    try:
        await notification_manager.connect(client_id, websocket)
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            notification_manager.disconnect(client_id)
    except Exception as e:
        notification_manager.disconnect(client_id)
        raise HTTPException(
            status_code=500,
            detail=f"WebSocket connection error: {str(e)}"
        )

@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    client_id: str,
    unread_only: bool = False,
    notification_manager: NotificationManager = Depends(get_notification_manager)
):
    """Get notifications for a client"""
    return notification_manager.get_notifications(client_id, unread_only)

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    client_id: str,
    notification_id: str,
    notification_manager: NotificationManager = Depends(get_notification_manager)
):
    """Mark a notification as read"""
    notification_manager.mark_as_read(client_id, notification_id)
    return {"status": "success"}