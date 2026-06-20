from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist

from app.models import ThresholdSettings
from app.schemas import ThresholdSettingsCreate, ThresholdSettingsResponse, StatusResponse

router = APIRouter(prefix="/api/thresholds", tags=["阈值设置"])


@router.post("/", response_model=ThresholdSettingsResponse, summary="创建阈值设置")
async def create_threshold_settings(data: ThresholdSettingsCreate):
    obj = await ThresholdSettings.create(**data.model_dump())
    return obj


@router.get("/latest", response_model=ThresholdSettingsResponse, summary="获取最新阈值设置")
async def get_latest_threshold_settings():
    obj = await ThresholdSettings.all().order_by("-updated_at").first()
    if not obj:
        default_data = ThresholdSettingsCreate()
        obj = await ThresholdSettings.create(**default_data.model_dump())
    return obj


@router.get("/", summary="获取阈值设置列表")
async def list_threshold_settings(limit: int = 50, offset: int = 0):
    data = await ThresholdSettings.all().limit(limit).offset(offset)
    return data


@router.put("/{setting_id}", response_model=ThresholdSettingsResponse, summary="更新阈值设置")
async def update_threshold_settings(setting_id: int, data: ThresholdSettingsCreate):
    try:
        obj = await ThresholdSettings.get(id=setting_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="设置不存在")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    await obj.save()
    return obj


@router.delete("/{setting_id}", response_model=StatusResponse, summary="删除阈值设置")
async def delete_threshold_settings(setting_id: int):
    deleted_count = await ThresholdSettings.filter(id=setting_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="设置不存在")
    return StatusResponse(status="success", message="删除成功")
