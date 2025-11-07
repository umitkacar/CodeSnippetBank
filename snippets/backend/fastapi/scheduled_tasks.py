"""Scheduled Background Tasks"""
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging

app = FastAPI()
scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

async def cleanup_task():
    """Cleanup task running every hour"""
    logger.info(f"Running cleanup task at {datetime.now()}")
    # Cleanup logic here

async def backup_task():
    """Backup task running daily"""
    logger.info(f"Running backup task at {datetime.now()}")
    # Backup logic here

async def health_check_task():
    """Health check running every 5 minutes"""
    logger.info(f"Health check at {datetime.now()}")

@app.on_event("startup")
async def startup_event():
    """Start scheduled tasks"""
    # Run every hour
    scheduler.add_job(cleanup_task, 'interval', hours=1)

    # Run daily at 2 AM
    scheduler.add_job(backup_task, 'cron', hour=2, minute=0)

    # Run every 5 minutes
    scheduler.add_job(health_check_task, 'interval', minutes=5)

    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduled tasks"""
    scheduler.shutdown()

@app.get("/tasks")
async def get_scheduled_tasks():
    """Get all scheduled tasks"""
    jobs = scheduler.get_jobs()
    return {
        "tasks": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time)
            }
            for job in jobs
        ]
    }
