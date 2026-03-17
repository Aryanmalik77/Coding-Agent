"""Email bus for the coding agent to bypass messaging limits."""

import os
import smtplib
import ssl
from email.message import EmailMessage
from loguru import logger

class EmailInterface:
    """
    Interface for sending full reports via Email.
    Used as a fallback for Telegram character limits.
    """

    def __init__(self, email_user: str, email_password: str):
        self.email_user = email_user
        self.email_password = email_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # SSL

    def send_report(self, subject: str, body: str, recipient: str) -> bool:
        """Send a full markdown report to a specific recipient."""
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.email_user
        msg["To"] = recipient

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            logger.info(f"[EMAIL-OUT] Success: Report '{subject}' sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"[EMAIL-ERR] Failed to send email to {recipient}: {e}")
            return False
