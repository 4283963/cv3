"""
阈值检查与告警生成工具
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.models import ThresholdSettings, MonitoringData
from app.schemas import AbnormalItem, AlertMessage
from app.ws_manager import alert_manager


METRIC_INFO = {
    "temperature": {"name": "水温", "unit": "°C"},
    "ph": {"name": "pH 值", "unit": ""},
    "dissolved_oxygen": {"name": "溶解氧", "unit": "mg/L"},
}

RANGE_KEYS = {
    "temperature": ("temp_min", "temp_max"),
    "ph": ("ph_min", "ph_max"),
    "dissolved_oxygen": ("do_min", "do_max"),
}


async def get_thresholds_for_pond(pond_id: Optional[int]) -> ThresholdSettings:
    """获取指定鱼塘的阈值,没有则取全局(pond_id 为 null)的最新一条"""
    if pond_id is not None:
        obj = await ThresholdSettings.filter(pond_id=pond_id).order_by("-updated_at").first()
        if obj:
            return obj
    obj = await ThresholdSettings.all().order_by("-updated_at").first()
    if obj:
        return obj
    return await ThresholdSettings.create(
        temp_min=15.0, temp_max=30.0,
        ph_min=6.5, ph_max=8.5,
        do_min=5.0, do_max=12.0,
    )


def check_value(metric: str, value: float, threshold: ThresholdSettings) -> Optional[dict]:
    min_key, max_key = RANGE_KEYS[metric]
    safe_min = getattr(threshold, min_key)
    safe_max = getattr(threshold, max_key)
    info = METRIC_INFO[metric]
    if value < safe_min:
        status = "low"
    elif value > safe_max:
        status = "high"
    else:
        return None
    return {
        "metric": metric,
        "metric_name": info["name"],
        "status": status,
        "value": value,
        "unit": info["unit"],
        "safe_min": safe_min,
        "safe_max": safe_max,
    }


async def check_and_notify(data: MonitoringData, threshold: ThresholdSettings):
    """检查监测数据是否超标,若超标则广播告警"""
    abnormals: List[dict] = []
    for metric in ("temperature", "ph", "dissolved_oxygen"):
        result = check_value(metric, getattr(data, metric), threshold)
        if result:
            abnormals.append(result)

    if not abnormals:
        return None

    alert_id = f"alert-{data.id}-{uuid.uuid4().hex[:8]}"
    alert = AlertMessage(
        type="alert",
        alert_id=alert_id,
        pond_id=getattr(data, "pond_id", None),
        pond_name=data.pond_name or "默认鱼塘",
        timestamp=datetime.now(timezone.utc),
        data_id=data.id,
        abnormals=[AbnormalItem(**a) for a in abnormals],
    )
    await alert_manager.broadcast_alert(alert.model_dump())
    return alert
