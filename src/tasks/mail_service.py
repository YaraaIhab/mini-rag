import datetime
from time import sleep
from datetime import datetime
from celery_app import celery_app
from helpers.config import get_settings
import logging
import asyncio

logger = logging.getLogger("celery_tasks")

@celery_app.task(bind=True, name="tasks.mail_service.send_email_report")
def send_email_report(self, mail_wait_seconds:int):
    # function to change the function to a celery task
    return asyncio.run(_send_email_report(self, mail_wait_seconds)) 

async def _send_email_report(task_instance, mail_wait_seconds:int):
    started_at = str(datetime.now()) # str because datetime is not JSON serializable, and Celery's meta expects JSON-serializable data
    
    task_instance.update_state(
        state='PROGRESS', 
        meta={'started_at': started_at}
    )
    
    for i in range(15):
        logger.info(f"Report {i+1} sent!")
        await asyncio.sleep(mail_wait_seconds) # Simulate time taken to send each report, with a delay of mail_wait_seconds seconds

    return {"success": True, 
            "message": "All reports sent successfully!", 
            'total': 15, 
            "end_time": str(datetime.now())
    }