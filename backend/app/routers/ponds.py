from fastapi import APIRouter, HTTPException
from tortoise.exceptions import DoesNotExist
from typing import List

from app.models import FishPond
from app.schemas import FishPondCreate, FishPondResponse, StatusResponse

router = APIRouter(prefix="/api/ponds", tags=["鱼塘管理"])


@router.post("/", response_model=FishPondResponse, summary="创建鱼塘")
async def create_pond(data: FishPondCreate):
    obj = await FishPond.create(**data.model_dump())
    return obj


@router.get("/", response_model=List[FishPondResponse], summary="获取鱼塘列表")
async def list_ponds():
    return await FishPond.all().order_by("id")


@router.get("/{pond_id}", response_model=FishPondResponse, summary="根据ID获取鱼塘")
async def get_pond(pond_id: int):
    try:
        return await FishPond.get(id=pond_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="鱼塘不存在")


@router.delete("/{pond_id}", response_model=StatusResponse, summary="删除鱼塘")
async def delete_pond(pond_id: int):
    deleted = await FishPond.filter(id=pond_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="鱼塘不存在")
    return StatusResponse(status="success", message="删除成功")
