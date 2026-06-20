import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws_manager import alert_manager

router = APIRouter(tags=["WebSocket 告警通道"])
logger = logging.getLogger("ws_router")


@router.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await alert_manager.connect(websocket)
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text('{"type":"pong"}')
            except asyncio.TimeoutError:
                await alert_manager.broadcast_heartbeat()
    except WebSocketDisconnect:
        logger.info("客户端主动断开")
    except Exception as e:
        logger.warning(f"WebSocket 异常: {e}")
    finally:
        await alert_manager.disconnect(websocket)
