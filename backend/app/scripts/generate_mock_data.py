"""
模拟数据生成脚本
支持多鱼塘轮流上报,通过 HTTP API 提交以触发后端告警检查
运行方式: python -m app.scripts.generate_mock_data
"""
import asyncio
import random
import httpx
from datetime import datetime
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.models import MonitoringData, ThresholdSettings, FishPond

API_BASE = "http://localhost:8000/api"
DEFAULT_PONDS = [
    {"name": "1号塘-锦鲤池", "location": "前院"},
    {"name": "2号塘-草鱼池", "location": "后院"},
    {"name": "3号塘-金鱼池", "location": "东侧"},
]


async def init_ponds_and_thresholds():
    ponds = await FishPond.all()
    if not ponds:
        for p in DEFAULT_PONDS:
            await FishPond.create(**p)
        ponds = await FishPond.all()
        print(f"✅ 已创建 {len(ponds)} 个默认鱼塘")
    else:
        print(f"ℹ️  已存在 {len(ponds)} 个鱼塘")

    for pond in ponds:
        existing = await ThresholdSettings.filter(pond_id=pond.id).first()
        if not existing:
            await ThresholdSettings.create(pond_id=pond.id)
            print(f"  ├─ 为「{pond.name}」创建默认阈值")


def generate_reading(pond_index: int):
    temp_base = 22.0 + pond_index * 0.5
    ph_base = 7.2
    do_base = 8.5

    temp = round(temp_base + random.uniform(-3, 3), 2)
    ph = round(ph_base + random.uniform(-0.8, 0.8), 2)
    do_oxygen = round(do_base + random.uniform(-2, 2), 2)

    if random.random() < 0.12:
        abnormal_type = random.choice(['temp_high', 'temp_low', 'ph_low', 'ph_high', 'do_low'])
        if abnormal_type == 'temp_high':
            temp = round(random.uniform(33, 39), 2)
        elif abnormal_type == 'temp_low':
            temp = round(random.uniform(8, 14), 2)
        elif abnormal_type == 'ph_low':
            ph = round(random.uniform(5.0, 6.2), 2)
        elif abnormal_type == 'ph_high':
            ph = round(random.uniform(9.0, 9.8), 2)
        elif abnormal_type == 'do_low':
            do_oxygen = round(random.uniform(2, 4.5), 2)

    return {
        'temperature': temp,
        'ph': ph,
        'dissolved_oxygen': do_oxygen
    }


async def submit_reading(client: httpx.AsyncClient, pond):
    reading = generate_reading(pond.id)
    payload = {
        "pond_id": pond.id,
        "pond_name": pond.name,
        **reading
    }
    try:
        resp = await client.post(f"{API_BASE}/monitoring/", json=payload, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] 📤 {pond.name} | "
                f"水温: {data['temperature']}°C | pH: {data['ph']} | DO: {data['dissolved_oxygen']}mg/L"
            )
        else:
            print(f"❌ 上报失败 [{resp.status_code}]: {resp.text}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")


async def generate_batch(client: httpx.AsyncClient, ponds, count=20):
    print(f"📦 开始生成 {count} 条历史监测数据...")
    for i in range(count):
        pond = ponds[i % len(ponds)]
        await submit_reading(client, pond)
    print(f"✅ 已生成 {count} 条历史数据\n")


async def continuous_generate(client: httpx.AsyncClient, ponds, interval=3):
    print(f"🔄 开始持续生成模拟数据 (间隔 {interval} 秒, {len(ponds)} 个鱼塘轮流)...")
    print("💡 现在请打开前端网页,观察告警弹窗")
    print("按 Ctrl+C 停止\n")
    idx = 0
    try:
        while True:
            pond = ponds[idx % len(ponds)]
            await submit_reading(client, pond)
            idx += 1
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 已停止生成模拟数据")


async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    await init_ponds_and_thresholds()
    print()

    ponds = await FishPond.all()

    async with httpx.AsyncClient() as client:
        existing_count = await MonitoringData.all().count()
        if existing_count == 0:
            await generate_batch(client, ponds, 20)
        await continuous_generate(client, ponds, 3)

    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
