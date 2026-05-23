"""バッチ実行用のログ設定（logs/ に1実行1ファイル）。"""

from __future__ import annotations

import logging
from pathlib import Path

from news_digest.settings import LOGS_DIR
from news_digest.time_jst import now_jst

# ログフォーマット（JST の時刻を含む）
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def log_file_path_for_now() -> Path:
    """例: logs/run-2026-05-21_060015.log（JST）"""
    ts = now_jst().strftime("%Y-%m-%d_%H%M%S")
    return LOGS_DIR / f"run-{ts}.log"


def setup_batch_logger() -> tuple[logging.Logger, Path]:
    """
    ルートロガーにファイル＋コンソール出力を設定する。

    Returns:
        (logger, ログファイルパス)
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = log_file_path_for_now()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    # google-genai / httpx の詳細ログはバッチログを見づらくするため抑制
    for noisy in ("google_genai", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # タイムスタンプを JST で出すため、各ハンドラの converter を差し替える
    jst_now = now_jst

    def _jst_converter(secs: float):
        return jst_now().timetuple()

    file_handler.converter = _jst_converter  # type: ignore[method-assign]
    console_handler.converter = _jst_converter  # type: ignore[method-assign]

    batch_logger = logging.getLogger("news_digest.batch")
    batch_logger.info("ログファイル: %s", log_path)
    return batch_logger, log_path
