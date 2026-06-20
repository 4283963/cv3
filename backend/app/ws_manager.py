"""
WebSocket 连接管理器
负责维护所有前端 WebSocket 连接,并在告警发生时主动推送
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Set
from fastapi import WebSocket

logger = logging.getLogger("alert_manager")


class AlertManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket 已连接, 当前在线: {len(self.active_connections)}")
        await self._send_to(websocket, {
            "type": "connected",
            "message": "告警通道已建立",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "online_clients": len(self.active_connections)
        })

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket 已断开, 当前在线: {len(self.active_connections)}")

    async def _send_to(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_text(json.dumps(data, ensure_ascii=False, default=str))
        except Exception as e:
            logger.warning(f"发送消息失败: {e}")
            await self.disconnect(websocket)

    async def broadcast_alert(self, alert: dict):
        """广播告警给所有连接的客户端"""
        if not self.active_connections:
            logger.info("当前无 WebSocket 连接, 告警仅记录日志")
            return
        message = json.dumps(alert, ensure_ascii=False, default=str)
        dead = []
        tasks = [conn.send_text(message) for conn in self.active_connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        async with self._lock:
            for conn, result in zip(list(self.active_connections), results):
                if isinstance(result, Exception):
                    dead.append(conn)
            for conn in dead:
                self.active_connections.discard(conn)
        if dead:
            logger.info(f"清理 {len(dead)} 个失效连接")
        logger.info(
            f"已推送告警 -> {len(self.active_connections)} 个客户端 | "
            f"鱼塘={alert.get('pond_name')} | "
            f"异常={[a.get('metric_name') for a in alert.get('abnormals', [])]}"
        )

    async def broadcast_heartbeat(self):
        if not self.active_connections:
            return
        message = json.dumps({
            "type": "heartbeat",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "online_clients": len(self.active_connections)
        }, ensure_ascii=False, default=str)
        dead = []
        async with self._lock:
            conns = list(self.active_connections)
        for conn in conns:
            try:
                await conn.send_text(message)
            except Exception:
                dead.append(conn)
        if dead:
            async with self._lock:
                for conn in dead:
                    self.active_connections.discard(conn)


alert_manager = AlertManager()
