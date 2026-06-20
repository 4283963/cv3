from datetime import datetime
from pydantic import BaseModel, Field


class MonitoringDataCreate(BaseModel):
    temperature: float = Field(..., description="水温 (°C)", ge=-10, le=50)
    ph: float = Field(..., description="pH值", ge=0, le=14)
    dissolved_oxygen: float = Field(..., description="溶解氧 (mg/L)", ge=0, le=20)


class MonitoringDataResponse(BaseModel):
    id: int
    temperature: float
    ph: float
    dissolved_oxygen: float
    created_at: datetime

    class Config:
        from_attributes = True


class ThresholdSettingsCreate(BaseModel):
    temp_min: float = Field(15.0, description="水温最小值", ge=-10, le=50)
    temp_max: float = Field(30.0, description="水温最大值", ge=-10, le=50)
    ph_min: float = Field(6.5, description="pH最小值", ge=0, le=14)
    ph_max: float = Field(8.5, description="pH最大值", ge=0, le=14)
    do_min: float = Field(5.0, description="溶解氧最小值", ge=0, le=20)
    do_max: float = Field(12.0, description="溶解氧最大值", ge=0, le=20)


class ThresholdSettingsResponse(BaseModel):
    id: int
    temp_min: float
    temp_max: float
    ph_min: float
    ph_max: float
    do_min: float
    do_max: float
    updated_at: datetime

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    status: str
    message: str
