"""
模拟数据生成脚本
用于在没有真实传感器的情况下生成模拟监测数据
运行方式: python -m app.scripts.generate_mock_data
"""
import asyncio
import random
import time
from datetime import datetime
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.models import MonitoringData, ThresholdSettings


async def init_thresholds():
    exists = await ThresholdSettings.first()
    if not exists:
        await ThresholdSettings.create(
            temp_min=15.0,
            temp_max=30.0,
            ph_min=6.5,
            ph_max=8.5,
            do_min=5.0,
            do_max=12.0
        )
        print("✅ 默认阈值设置已创建")
    else:
        print("ℹ️  阈值设置已存在")


def generate_reading():
    temp_base = 22.0
    ph_base = 7.2
    do_base = 8.5

    temp = round(temp_base + random.uniform(-3, 3), 2)
    ph = round(ph_base + random.uniform(-0.8, 0.8), 2)
    do_oxygen = round(do_base + random.uniform(-2, 2), 2)

    if random.random() < 0.08:
        abnormal_type = random.choice(['temp_high', 'temp_low', 'ph_low', 'do_low'])
        if abnormal_type == 'temp_high':
            temp = round(random.uniform(31, 35), 2)
        elif abnormal_type == 'temp_low':
            temp = round(random.uniform(8, 14), 2)
        elif abnormal_type == 'ph_low':
            ph = round(random.uniform(5.0, 6.2), 2)
        elif abnormal_type == 'do_low':
            do_oxygen = round(random.uniform(2, 4.5), 2)

    return {
        'temperature': temp,
        'ph': ph,
        'dissolved_oxygen': do_oxygen
    }


async def generate_once():
    reading = generate_reading()
    data = await MonitoringData.create(**reading)
    print(f"[{data.created_at.strftime('%H:%M:%S')}] 水温: {data.temperature}°C | pH: {data.ph} | DO: {data.dissolved_oxygen}mg/L")
    return data


async def generate_batch(count=50):
    print(f"📦 开始生成 {count} 条历史监测数据...")
    for _ in range(count):
        reading = generate_reading()
        await MonitoringData.create(**reading)
    print(f"✅ 已生成 {count} 条历史数据")


async def continuous_generate(interval=3):
    print(f"🔄 开始持续生成模拟数据 (间隔 {interval} 秒)...")
    print("按 Ctrl+C 停止\n")
    try:
        while True:
            await generate_once()
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 已停止生成模拟数据")


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    await init_thresholds()
    print()

    existing_count = await MonitoringData.all().count()
    if existing_count == 0:
        await generate_batch(50)
        print()

    await continuous_generate(3)

    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
