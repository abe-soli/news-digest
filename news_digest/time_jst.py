"""日付・時刻はすべて日本時間（JST）で扱う。"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> datetime:
    """現在の日時（JST）。"""
    return datetime.now(JST)


def today_jst() -> date:
    """今日の日付（JST）。"""
    return now_jst().date()


def format_date(d: date) -> str:
    """JSONファイル名用: YYYY-MM-DD。"""
    return d.isoformat()


def digest_filename(d: date) -> str:
    """例: digest-2026-05-20.json"""
    return f"digest-{format_date(d)}.json"
