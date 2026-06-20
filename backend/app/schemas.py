from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FishPondCreate(BaseModel):
    name: str = Field(..., description="鱼塘名称", max_length=100)
    location: Optional[str] = Field(None, description="鱼塘位置", max_length=200)


class FishPondResponse(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MonitoringDataCreate(BaseModel):
    pond_id: Optional[int] = Field(None, description="所属鱼塘ID")
    pond_name: Optional[str] = Field("默认鱼塘", description="鱼塘名称")
    temperature: float = Field(..., description="水温 (°C)", ge=-10, le=50)
    ph: float = Field(..., description="pH值", ge=0, le=14)
    dissolved_oxygen: float = Field(..., description="溶解氧 (mg/L)", ge=0, le=20)


class MonitoringDataResponse(BaseModel):
    id: int
    pond_id: Optional[int] = None
    pond_name: str
    temperature: float
    ph: float
    dissolved_oxygen: float
    created_at: datetime

    class Config:
        from_attributes = True


class ThresholdSettingsCreate(BaseModel):
    pond_id: Optional[int] = Field(None, description="所属鱼塘ID")
    temp_min: float = Field(15.0, description="水温最小值", ge=-10, le=50)
    temp_max: float = Field(30.0, description="水温最大值", ge=-10, le=50)
    ph_min: float = Field(6.5, description="pH最小值", ge=0, le=14)
    ph_max: float = Field(8.5, description="pH最大值", ge=0, le=14)
    do_min: float = Field(5.0, description="溶解氧最小值", ge=0, le=20)
    do_max: float = Field(12.0, description="溶解氧最大值", ge=0, le=20)


class ThresholdSettingsResponse(BaseModel):
    id: int
    pond_id: Optional[int] = None
    temp_min: float
    temp_max: float
    ph_min: float
    ph_max: float
    do_min: float
    do_max: float
    updated_at: datetime

    class Config:
        from_attributes = True


class AbnormalItem(BaseModel):
    metric: str = Field(..., description="指标键: temperature/ph/dissolved_oxygen")
    metric_name: str = Field(..., description="指标中文名")
    status: str = Field(..., description="low/high")
    value: float = Field(..., description="当前值")
    unit: str = Field(..., description="单位")
    safe_min: float = Field(..., description="安全下限")
    safe_max: float = Field(..., description="安全上限")


class AlertMessage(BaseModel):
    type: str = Field("alert", description="消息类型: alert/resolved/heartbeat")
    alert_id: str = Field(..., description="告警唯一ID")
    pond_id: Optional[int] = None
    pond_name: str = Field(..., description="鱼塘名称")
    timestamp: datetime = Field(..., description="告警时间")
    data_id: Optional[int] = None
    abnormals: List[AbnormalItem] = Field(..., description="异常指标列表")


class StatusResponse(BaseModel):
    status: str
    message: str
