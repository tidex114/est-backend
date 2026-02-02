"""
Email Service for Sending Verification Emails
Can be extended to use SendGrid, Mailgun, etc.
"""
from abc import ABC, abstractmethod
from uuid import UUID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from services.auth.src.core.settings import settings


class EmailService(ABC):
    """Abstract base for email services"""

    @abstractmethod
    def send_verification_email(self, email: str, verification_token: str, user_id: UUID) -> bool:
        """Send verification email. Returns True if successful."""
        pass


class MockEmailService(EmailService):
    """Development email service that logs instead of sending"""

    def send_verification_email(self, email: str, verification_token: str, user_id: UUID) -> bool:
        """Log verification email instead of sending"""
        print(f"\n[MOCK EMAIL]")
        print(f"To: {email}")
        print(f"Subject: Verify your EST account")
        print(f"Verification Token: {verification_token}")
        print(f"User ID: {user_id}")
        print(f"Verification URL: {settings.auth_service_url}/auth/verify-email?token={verification_token}")
        print(f"[END MOCK EMAIL]\n")
        return True


class SMTPEmailService(EmailService):
    """SMTP email service for production"""

    def send_verification_email(self, email: str, verification_token: str, user_id: UUID) -> bool:
        """Send verification email via SMTP"""
        try:
            verification_url = f"{settings.auth_service_url}/auth/verify-email?token={verification_token}"

            subject = "Verify your EST account"
            html_body = f"""
            <html>
                <body>
                    <h1>Welcome to EST!</h1>
                    <p>Please verify your email address by clicking the link below:</p>
                    <a href="{verification_url}">Verify Email</a>
                    <p>Or copy this link: {verification_url}</p>
                    <p>This link expires in 24 hours.</p>
                </body>
            </html>
            """

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_from_email
            msg["To"] = email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            # Send
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_user:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)

                server.sendmail(settings.smtp_from_email, [email], msg.as_string())

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


def get_email_service() -> EmailService:
    """Factory to get appropriate email service based on environment"""
    if settings.env == "dev":
        return MockEmailService()
    else:
        return SMTPEmailService()
