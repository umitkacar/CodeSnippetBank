"""Email Service Implementation"""
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = FastAPI()

# Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-password"

# Models
class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    html: Optional[bool] = False
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None

class EmailWithTemplate(BaseModel):
    to: List[EmailStr]
    subject: str
    template_name: str
    template_data: dict

# Email service
class EmailService:
    """Email service for sending emails"""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ):
        """Send email"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject

        if cc:
            msg['Cc'] = ', '.join(cc)

        # Attach body
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # Connect and send
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)

                recipients = to + (cc or []) + (bcc or [])
                server.send_message(msg, to_addrs=recipients)

            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

email_service = EmailService(SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)

# Email templates
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to our platform!",
        "body": """
        <html>
            <body>
                <h1>Welcome {name}!</h1>
                <p>Thank you for joining our platform.</p>
                <p>Get started by visiting your dashboard.</p>
            </body>
        </html>
        """
    },
    "reset_password": {
        "subject": "Password Reset Request",
        "body": """
        <html>
            <body>
                <h1>Password Reset</h1>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>This link expires in 1 hour.</p>
            </body>
        </html>
        """
    }
}

# Endpoints
@app.post("/send-email")
async def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks
):
    """Send email"""
    background_tasks.add_task(
        email_service.send_email,
        to=email_request.to,
        subject=email_request.subject,
        body=email_request.body,
        html=email_request.html,
        cc=email_request.cc,
        bcc=email_request.bcc
    )

    return {"message": "Email queued for sending"}

@app.post("/send-template-email")
async def send_template_email(
    email_request: EmailWithTemplate,
    background_tasks: BackgroundTasks
):
    """Send email using template"""
    if email_request.template_name not in EMAIL_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {email_request.template_name} not found"
        )

    template = EMAIL_TEMPLATES[email_request.template_name]
    subject = template["subject"]
    body = template["body"].format(**email_request.template_data)

    background_tasks.add_task(
        email_service.send_email,
        to=email_request.to,
        subject=subject,
        body=body,
        html=True
    )

    return {"message": "Template email queued for sending"}

@app.post("/send-welcome-email")
async def send_welcome_email(
    email: EmailStr,
    name: str,
    background_tasks: BackgroundTasks
):
    """Send welcome email"""
    template = EMAIL_TEMPLATES["welcome"]
    subject = template["subject"]
    body = template["body"].format(name=name)

    background_tasks.add_task(
        email_service.send_email,
        to=[email],
        subject=subject,
        body=body,
        html=True
    )

    return {"message": f"Welcome email sent to {email}"}
