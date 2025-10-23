from arq import create_pool
from arq.connections import RedisSettings
from backend.config import settings
import asyncio

async def sync_broker_task(ctx, broker_account_id: int, user_id: int):
    """ARQ task for syncing broker data."""
    from backend.services.ibkr_sync import sync_broker_data
    await sync_broker_data(broker_account_id, user_id)

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = [sync_broker_task]
    max_jobs = 10
    job_timeout = 300  # 5 minutes