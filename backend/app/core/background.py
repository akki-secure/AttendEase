import logging
from typing import Callable

logger = logging.getLogger(__name__)


def send_emails_background(emails: list[tuple[Callable, tuple]]) -> None:
    """バックグラウンドスレッドでメールを順に送信する。失敗してもログのみ。"""
    for fn, args in emails:
        try:
            fn(*args)
        except Exception:
            logger.exception("バックグラウンドメール送信に失敗しました: %s", getattr(fn, "__name__", fn))
