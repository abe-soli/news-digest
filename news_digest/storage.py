"""日付ごとのダイジェストJSONの読み書き（Step 1 では読み込み中心）。"""

import json
from datetime import date
from pathlib import Path

from news_digest.settings import DATA_DIR, RETENTION_DAYS
from news_digest.time_jst import digest_filename, format_date, today_jst

# 本番データが無いときに表示するサンプル（git に含める）
SAMPLE_DIGEST_PATH = DATA_DIR / "sample-digest.json"


def digest_path_for(d: date) -> Path:
    return DATA_DIR / digest_filename(d)


def load_digest(d: date | None = None) -> tuple[dict | None, bool]:
    """
    指定日のダイジェストを読み込む。
    戻り値: (データ, サンプル表示か)
    """
    target = d or today_jst()
    path = digest_path_for(target)

    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return json.load(f), False

    if SAMPLE_DIGEST_PATH.is_file():
        with SAMPLE_DIGEST_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        # 表示用に日付だけ合わせる
        data = {**data, "date": format_date(target)}
        return data, True

    return None, False


def list_digest_dates() -> list[str]:
    """data/ 内の digest-YYYY-MM-DD.json の日付一覧（新しい順）。"""
    dates: list[str] = []
    for path in DATA_DIR.glob("digest-*.json"):
        name = path.stem  # digest-2026-05-20
        if name.startswith("digest-"):
            dates.append(name.removeprefix("digest-"))
    dates.sort(reverse=True)
    return dates


def save_digest(digest: dict, d: date | None = None) -> Path:
    """
    ダイジェスト dict を JSON ファイルへ保存する。
    data/ が無ければ作成する。d を省略すると当日（JST）のファイル名にそろえる。
    """
    target = d or today_jst()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    digest.setdefault("date", format_date(target))
    path = digest_path_for(target)
    with path.open("w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)
    return path


def prune_old_digests(days: int | None = None) -> int:
    """
    data/digest-*.json のうち、保持日数（デフォルト RETENTION_DAYS）を超えたものを削除する。

    Returns:
        削除したファイル数
    """
    keep = days if days is not None else RETENTION_DAYS
    today = today_jst()
    removed = 0
    for path in DATA_DIR.glob("digest-*.json"):
        stem = path.stem
        if not stem.startswith("digest-"):
            continue
        try:
            file_date = date.fromisoformat(stem.removeprefix("digest-"))
        except ValueError:
            continue
        if (today - file_date).days > keep:
            path.unlink(missing_ok=True)
            removed += 1
    return removed
