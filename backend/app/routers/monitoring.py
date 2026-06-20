from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist
from typing import List, Optional

from app.models import MonitoringData
from app.schemas import MonitoringDataCreate, MonitoringDataResponse, StatusResponse
from app.alert_service import get_thresholds_for_pond, check_and_notify

router = APIRouter(prefix="/api/monitoring", tags=["实时监测数据"])


@router.post("/", response_model=MonitoringDataResponse, summary="新增监测数据(触发告警检查)")
async def create_monitoring_data(data: MonitoringDataCreate):
    payload = data.model_dump(exclude_unset=False)
    pond_id = payload.get("pond_id")
    if not payload.get("pond_name"):
        payload["pond_name"] = "默认鱼塘"
    obj = await MonitoringData.create(**payload)
    await obj.refresh_from_db()

    threshold = await get_thresholds_for_pond(pond_id)
    await check_and_notify(obj, threshold)
    return obj


@router.get("/latest", response_model=MonitoringDataResponse, summary="获取最新一条监测数据")
async def get_latest_monitoring_data(pond_id: Optional[int] = None):
    qs = MonitoringData.all()
    if pond_id is not None:
        qs = qs.filter(pond_id=pond_id)
    obj = await qs.order_by("-created_at").first()
    if not obj:
        raise HTTPException(status_code=404, detail="暂无监测数据")
    return obj


@router.get("/", response_model=List[MonitoringDataResponse], summary="获取监测数据列表")
async def list_monitoring_data(limit: int = 100, offset: int = 0, pond_id: Optional[int] = None):
    qs = MonitoringData.all()
    if pond_id is not None:
        qs = qs.filter(pond_id=pond_id)
    data = await qs.order_by("-created_at").limit(limit).offset(offset)
    return data


@router.get("/{data_id}", response_model=MonitoringDataResponse, summary="根据ID获取监测数据")
async def get_monitoring_data(data_id: int):
    try:
        obj = await MonitoringData.get(id=data_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@router.delete("/{data_id}", response_model=StatusResponse, summary="删除监测数据")
async def delete_monitoring_data(data_id: int):
    deleted_count = await MonitoringData.filter(id=data_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="数据不存在")
    return StatusResponse(status="success", message="删除成功")
