"""
毎朝の自動実行用エントリポイント（Step 4）。

Windows タスクスケジューラからこのスクリプトを実行する想定。
logs/ に実行ごとのログファイルを残し、成功・失敗を記録する。

使い方:
  cd プロジェクトのルート
  python run_batch.py
"""

from __future__ import annotations

import os
import sys

from news_digest.batch_logging import setup_batch_logger
from news_digest.pipeline import run_digest_pipeline
from news_digest.settings import PROJECT_ROOT


def main() -> int:
    # タスクスケジューラは作業フォルダが不定なことがあるため、プロジェクト直下に移す
    os.chdir(PROJECT_ROOT)

    batch_logger, log_path = setup_batch_logger()
    batch_logger.info("バッチ開始 (cwd=%s)", os.getcwd())

    result = run_digest_pipeline()

    if result.success:
        batch_logger.info(
            "バッチ成功 | 取得 %d -> 採用 %d (除外 %d) | Gemini失敗 %d | 保存 %s | 削除 %d",
            result.raw_count,
            result.adopted_count,
            result.rejected_count,
            result.gemini_failures,
            result.saved_path,
            result.removed_old,
        )
        if result.rejected_samples:
            batch_logger.info("除外サンプル（最大10件）:")
            for reason, title in result.rejected_samples:
                batch_logger.info("  - %s: %s", reason, title)
        batch_logger.info("ログファイル: %s", log_path)
        return 0

    batch_logger.error("バッチ失敗: %s", result.error_message or "不明なエラー")
    batch_logger.info("ログファイル: %s", log_path)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
