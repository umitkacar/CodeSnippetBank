"""Background Tasks Implementation"""
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import asyncio
from datetime import datetime, timezone
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class EmailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    body: str

class NotificationSchema(BaseModel):
    user_id: str
    message: str
    notification_type: str = "info"

class ReportRequest(BaseModel):
    report_type: str
    parameters: dict
    recipient: EmailStr

# Background task functions
async def send_email(email: EmailSchema):
    """Simulate sending an email"""
    logger.info(f"Sending email to {email.recipient}")
    await asyncio.sleep(2)  # Simulate email sending delay
    logger.info(f"Email sent to {email.recipient}: {email.subject}")

async def process_notification(notification: NotificationSchema):
    """Process and send notification"""
    logger.info(f"Processing notification for user {notification.user_id}")
    await asyncio.sleep(1)
    logger.info(f"Notification sent to {notification.user_id}: {notification.message}")

async def generate_report(report_request: ReportRequest):
    """Generate a report in the background"""
    logger.info(f"Starting report generation: {report_request.report_type}")
    await asyncio.sleep(5)  # Simulate report generation
    logger.info(f"Report {report_request.report_type} generated successfully")

    # Send report via email
    await send_email(EmailSchema(
        recipient=report_request.recipient,
        subject=f"Report: {report_request.report_type}",
        body=f"Your report has been generated with parameters: {report_request.parameters}"
    ))

async def cleanup_old_data():
    """Cleanup old data from database"""
    logger.info("Starting data cleanup task")
    await asyncio.sleep(3)
    logger.info("Data cleanup completed")

def write_log(message: str):
    """Write log entry (synchronous)"""
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"[{timestamp}] {message}")

async def process_large_file(filename: str, user_id: str):
    """Process a large file in the background"""
    logger.info(f"Starting file processing: {filename}")

    # Simulate processing steps
    steps = ["Validating", "Parsing", "Transforming", "Saving"]
    for step in steps:
        logger.info(f"{step} {filename}...")
        await asyncio.sleep(2)

    logger.info(f"File processing completed: {filename}")

    # Send completion notification
    await process_notification(NotificationSchema(
        user_id=user_id,
        message=f"File {filename} processed successfully",
        notification_type="success"
    ))

# API Endpoints
@app.post("/send-email/")
async def send_email_endpoint(
    email: EmailSchema,
    background_tasks: BackgroundTasks
):
    """Send email in the background"""
    background_tasks.add_task(send_email, email)
    return {"message": "Email will be sent in the background"}

@app.post("/send-notification/")
async def send_notification(
    notification: NotificationSchema,
    background_tasks: BackgroundTasks
):
    """Send notification in the background"""
    background_tasks.add_task(process_notification, notification)
    return {"message": "Notification queued for processing"}

@app.post("/generate-report/")
async def generate_report_endpoint(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """Generate report in the background"""
    background_tasks.add_task(generate_report, report_request)
    return {
        "message": "Report generation started",
        "report_type": report_request.report_type,
        "recipient": report_request.recipient
    }

@app.post("/process-file/")
async def process_file_endpoint(
    filename: str,
    user_id: str,
    background_tasks: BackgroundTasks
):
    """Process file in the background"""
    background_tasks.add_task(process_large_file, filename, user_id)
    return {"message": f"File {filename} queued for processing"}

@app.post("/signup/")
async def signup(
    email: EmailStr,
    username: str,
    background_tasks: BackgroundTasks
):
    """User signup with welcome email"""
    # Create user logic here
    user_id = "user_123"

    # Add multiple background tasks
    background_tasks.add_task(
        send_email,
        EmailSchema(
            recipient=email,
            subject="Welcome to our platform!",
            body=f"Hello {username}, welcome to our platform!"
        )
    )

    background_tasks.add_task(
        write_log,
        f"New user signup: {username} ({email})"
    )

    background_tasks.add_task(
        process_notification,
        NotificationSchema(
            user_id=user_id,
            message="Welcome! Complete your profile to get started.",
            notification_type="info"
        )
    )

    return {
        "message": "Signup successful",
        "user_id": user_id,
        "username": username
    }

@app.post("/cleanup/")
async def trigger_cleanup(background_tasks: BackgroundTasks):
    """Trigger data cleanup"""
    background_tasks.add_task(cleanup_old_data)
    return {"message": "Cleanup task started"}

@app.post("/batch-emails/")
async def send_batch_emails(
    emails: List[EmailSchema],
    background_tasks: BackgroundTasks
):
    """Send multiple emails in the background"""
    for email in emails:
        background_tasks.add_task(send_email, email)

    return {
        "message": f"{len(emails)} emails queued for sending",
        "count": len(emails)
    }
