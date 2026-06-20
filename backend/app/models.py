from tortoise import fields
from tortoise.models import Model


class MonitoringData(Model):
    id = fields.IntField(pk=True)
    temperature = fields.FloatField(description="水温 (°C)")
    ph = fields.FloatField(description="pH值")
    dissolved_oxygen = fields.FloatField(description="溶解氧 (mg/L)")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "monitoring_data"
        ordering = ["-created_at"]


class ThresholdSettings(Model):
    id = fields.IntField(pk=True)
    temp_min = fields.FloatField(default=15.0, description="水温最小值")
    temp_max = fields.FloatField(default=30.0, description="水温最大值")
    ph_min = fields.FloatField(default=6.5, description="pH最小值")
    ph_max = fields.FloatField(default=8.5, description="pH最大值")
    do_min = fields.FloatField(default=5.0, description="溶解氧最小值")
    do_max = fields.FloatField(default=12.0, description="溶解氧最大值")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "threshold_settings"
