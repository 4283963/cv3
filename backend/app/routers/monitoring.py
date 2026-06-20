from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist
from typing import List

from app.models import MonitoringData
from app.schemas import MonitoringDataCreate, MonitoringDataResponse, StatusResponse

router = APIRouter(prefix="/api/monitoring", tags=["实时监测数据"])


@router.post("/", response_model=MonitoringDataResponse, summary="新增监测数据")
async def create_monitoring_data(data: MonitoringDataCreate):
    obj = await MonitoringData.create(**data.model_dump())
    return obj


@router.get("/latest", response_model=MonitoringDataResponse, summary="获取最新一条监测数据")
async def get_latest_monitoring_data():
    obj = await MonitoringData.first().order_by("-created_at")
    if not obj:
        raise HTTPException(status_code=404, detail="暂无监测数据")
    return obj


@router.get("/", response_model=List[MonitoringDataResponse], summary="获取监测数据列表")
async def list_monitoring_data(limit: int = 100, offset: int = 0):
    data = await MonitoringData.all().limit(limit).offset(offset)
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
