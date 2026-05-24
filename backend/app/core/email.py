import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


def send_otp_email(to_address: str, otp_code: str) -> None:
    """Gmail SMTP（STARTTLS）でOTP認証コードを送信する"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "【AttendEase】ログイン認証コード"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_address

    expire_min = settings.OTP_EXPIRE_MINUTES
    text = f"認証コード: {otp_code}\n有効期限: {expire_min}分\n\nこのコードは第三者に教えないでください。"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:#1d4ed8">AttendEase ログイン認証</h2>
  <p>以下の認証コードを入力してください。</p>
  <div style="font-size:2rem;font-weight:bold;letter-spacing:0.3em;padding:16px;background:#f1f5f9;border-radius:8px;text-align:center">
    {otp_code}
  </div>
  <p style="color:#64748b;font-size:0.875rem">有効期限: <strong>{expire_min}分</strong><br>このコードは第三者に教えないでください。</p>
</div>"""

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to_address, msg.as_string())
