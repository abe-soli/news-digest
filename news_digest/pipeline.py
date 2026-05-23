"""ダイジェスト生成パイプライン（手動実行・バッチ共通）。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from news_digest.filtering import filter_articles
from news_digest.gemini_summarizer import enrich_articles_with_gemini
from news_digest.rss_fetch import fetch_articles_from_rss
from news_digest.settings import GEMINI_API_KEY
from news_digest.storage import prune_old_digests, save_digest
from news_digest.time_jst import format_date, now_jst, today_jst

logger = logging.getLogger(__name__)


@dataclass
class DigestRunResult:
    """1回の実行結果（ログ出力・終了コード判定用）。"""

    success: bool
    saved_path: Path | None = None
    raw_count: int = 0
    adopted_count: int = 0
    rejected_count: int = 0
    removed_old: int = 0
    gemini_failures: int = 0
    rejected_samples: list[tuple[str, str]] = field(default_factory=list)
    error_message: str | None = None


def run_digest_pipeline() -> DigestRunResult:
    """
    RSS取得 → フィルタ → Gemini要約 → JSON保存 → 古いファイル削除。

    例外が出た場合は DigestRunResult.success=False と error_message を返す。
    """
    result = DigestRunResult(success=False)
    try:
        if not GEMINI_API_KEY:
            logger.warning(
                "GEMINI_API_KEY が未設定です。要約・用語は RSS 本文のまま保存されます。"
            )

        logger.info("RSS 取得を開始します")
        raw_articles = fetch_articles_from_rss()
        result.raw_count = len(raw_articles)
        logger.info("RSS 取得完了: %d 件", result.raw_count)

        filtered_articles, rejected_articles = filter_articles(raw_articles)
        result.rejected_count = len(rejected_articles)
        logger.info(
            "フィルタ完了: 採用 %d 件 / 除外 %d 件",
            len(filtered_articles),
            result.rejected_count,
        )

        for item in rejected_articles[:10]:
            title = str(item.get("title") or "(無題)")
            reason = str(item.get("_filter_reason") or "unknown")
            result.rejected_samples.append((reason, title))
            logger.debug("除外: %s | %s", reason, title)

        logger.info("Gemini 要約を開始します（記事数: %d）", len(filtered_articles))
        articles, gemini_failures = enrich_articles_with_gemini(filtered_articles)
        result.gemini_failures = gemini_failures
        result.adopted_count = len(articles)
        if gemini_failures:
            logger.warning("Gemini 要約に失敗した記事: %d 件（RSS要約のまま保存）", gemini_failures)

        digest = {
            "date": format_date(today_jst()),
            "generated_at": now_jst().isoformat(timespec="seconds"),
            "articles": articles,
        }
        path = save_digest(digest)
        result.saved_path = path
        logger.info("JSON 保存完了: %s", path)

        result.removed_old = prune_old_digests()
        if result.removed_old:
            logger.info("古いダイジェストを削除: %d 件", result.removed_old)

        result.success = True
        return result

    except Exception as exc:
        result.error_message = str(exc)
        logger.exception("ダイジェスト生成でエラーが発生しました")
        return result
