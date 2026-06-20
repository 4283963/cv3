from tortoise import fields
from tortoise.models import Model


class FishPond(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="鱼塘名称")
    location = fields.CharField(max_length=200, null=True, description="鱼塘位置")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "fish_pond"
        ordering = ["id"]


class MonitoringData(Model):
    id = fields.IntField(pk=True)
    pond = fields.ForeignKeyField("models.FishPond", related_name="monitoring_data", null=True, description="所属鱼塘")
    pond_name = fields.CharField(max_length=100, default="默认鱼塘", description="鱼塘名称(冗余字段,便于推送)")
    temperature = fields.FloatField(description="水温 (°C)")
    ph = fields.FloatField(description="pH值")
    dissolved_oxygen = fields.FloatField(description="溶解氧 (mg/L)")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "monitoring_data"
        ordering = ["-created_at"]


class ThresholdSettings(Model):
    id = fields.IntField(pk=True)
    pond = fields.ForeignKeyField("models.FishPond", related_name="threshold_settings", null=True, description="所属鱼塘")
    temp_min = fields.FloatField(default=15.0, description="水温最小值")
    temp_max = fields.FloatField(default=30.0, description="水温最大值")
    ph_min = fields.FloatField(default=6.5, description="pH最小值")
    ph_max = fields.FloatField(default=8.5, description="pH最大值")
    do_min = fields.FloatField(default=5.0, description="溶解氧最小值")
    do_max = fields.FloatField(default=12.0, description="溶解氧最大值")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "threshold_settings"
