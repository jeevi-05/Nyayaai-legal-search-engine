from email.message import EmailMessage
import smtplib
from contextlib import closing

from app.core.config import get_settings


def send_verification_email(recipient: str, full_name: str, otp: str) -> None:
    settings = get_settings()
    if not all((settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.SMTP_FROM_EMAIL)):
        raise RuntimeError("SMTP email delivery is not configured on the backend")

    message = EmailMessage()
    message["Subject"] = "NyayaAI Email Verification Code"
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = recipient
    message.set_content(
        f"Hello {full_name},\n\n"
        "Your NyayaAI verification code is:\n\n"
        f"{otp}\n\n"
        "This code will expire in 5 minutes.\n\n"
        "If you did not request this registration, you can ignore this email.\n\n"
        "Regards,\nNyayaAI Legal Intelligence Platform"
    )

    # Gmail uses STARTTLS on port 587. SSL is available for providers that use
    # implicit TLS (usually port 465).
    smtp_class = smtplib.SMTP_SSL if settings.SMTP_USE_SSL else smtplib.SMTP
    with closing(smtp_class(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.SMTP_TIMEOUT_SECONDS)) as smtp:
        if not settings.SMTP_USE_SSL:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(message)
