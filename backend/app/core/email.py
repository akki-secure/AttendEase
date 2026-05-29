import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def _send(to_address: str, subject: str, text: str, html: str) -> None:
    """Gmail SMTP（STARTTLS）でメールを送信する。失敗してもログのみ。"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info("SMTP未設定のためメール送信をスキップ: %s", subject)
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_address
        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_address, msg.as_string())
    except Exception:
        logger.exception("メール送信に失敗しました: %s → %s", subject, to_address)


def send_otp_email(to_address: str, otp_code: str) -> None:
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
    _send(to_address, "【AttendEase】ログイン認証コード", text, html)


def send_leave_request_email(to_address: str, applicant_name: str, leave_type: str, start: str, end: str) -> None:
    subject = "【AttendEase】休暇申請が届きました"
    text = f"{applicant_name} さんから休暇申請が届きました。\n種別: {leave_type}\n期間: {start} ～ {end}\n\nAttendEaseにログインして承認してください。"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:#1d4ed8">AttendEase 休暇申請通知</h2>
  <p><strong>{applicant_name}</strong> さんから休暇申請が届きました。</p>
  <table style="border-collapse:collapse;width:100%">
    <tr><td style="padding:6px;color:#64748b">種別</td><td style="padding:6px">{leave_type}</td></tr>
    <tr><td style="padding:6px;color:#64748b">期間</td><td style="padding:6px">{start} ～ {end}</td></tr>
  </table>
  <p>AttendEaseにログインして承認・否認してください。</p>
</div>"""
    _send(to_address, subject, text, html)


def send_leave_reviewed_email(to_address: str, applicant_name: str, status: str, comment: str | None, start: str, end: str) -> None:
    status_ja = "承認" if status == "APPROVED" else "否認"
    subject = f"【AttendEase】休暇申請が{status_ja}されました"
    comment_text = f"\nコメント: {comment}" if comment else ""
    text = f"{applicant_name} さん\n\n休暇申請（{start} ～ {end}）が{status_ja}されました。{comment_text}"
    color = "#16a34a" if status == "APPROVED" else "#dc2626"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:{color}">AttendEase 休暇申請{status_ja}</h2>
  <p>{applicant_name} さん</p>
  <p>休暇申請（{start} ～ {end}）が<strong>{status_ja}</strong>されました。</p>
  {"<p style='color:#64748b'>コメント: " + comment + "</p>" if comment else ""}
</div>"""
    _send(to_address, subject, text, html)


def send_overtime_request_email(to_address: str, applicant_name: str, date: str, minutes: int) -> None:
    hours = minutes // 60
    mins = minutes % 60
    duration = f"{hours}時間{mins}分" if hours else f"{mins}分"
    subject = "【AttendEase】残業申請が届きました"
    text = f"{applicant_name} さんから残業申請が届きました。\n日付: {date}\n時間: {duration}\n\nAttendEaseにログインして承認してください。"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:#1d4ed8">AttendEase 残業申請通知</h2>
  <p><strong>{applicant_name}</strong> さんから残業申請が届きました。</p>
  <table style="border-collapse:collapse;width:100%">
    <tr><td style="padding:6px;color:#64748b">日付</td><td style="padding:6px">{date}</td></tr>
    <tr><td style="padding:6px;color:#64748b">残業時間</td><td style="padding:6px">{duration}</td></tr>
  </table>
  <p>AttendEaseにログインして承認・否認してください。</p>
</div>"""
    _send(to_address, subject, text, html)


def send_overtime_reviewed_email(to_address: str, applicant_name: str, status: str, comment: str | None, date: str) -> None:
    status_ja = "承認" if status == "APPROVED" else "否認"
    subject = f"【AttendEase】残業申請が{status_ja}されました"
    comment_text = f"\nコメント: {comment}" if comment else ""
    text = f"{applicant_name} さん\n\n残業申請（{date}）が{status_ja}されました。{comment_text}"
    color = "#16a34a" if status == "APPROVED" else "#dc2626"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:{color}">AttendEase 残業申請{status_ja}</h2>
  <p>{applicant_name} さん</p>
  <p>残業申請（{date}）が<strong>{status_ja}</strong>されました。</p>
  {"<p style='color:#64748b'>コメント: " + comment + "</p>" if comment else ""}
</div>"""
    _send(to_address, subject, text, html)


def send_overtime_alert_email(to_address: str, user_name: str, year: int, month: int, total_minutes: int) -> None:
    total_h = round(total_minutes / 60, 1)
    subject = f"【AttendEase】残業時間アラート（{year}年{month}月）"
    text = f"{user_name} さんの{year}年{month}月の残業時間が {total_h}h に達しました。36協定の上限をご確認ください。"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:#dc2626">AttendEase 残業アラート</h2>
  <p><strong>{user_name}</strong> さんの{year}年{month}月の残業時間が <strong>{total_h}h</strong> に達しました。</p>
  <p style="color:#64748b">36協定の月45h上限をご確認ください。</p>
</div>"""
    _send(to_address, subject, text, html)
