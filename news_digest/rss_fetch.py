"""
RSS フィードから記事リストを組み立てる（Gemini 要約の前段階）。

config/sources.yaml の一覧を読み、各ソースから最大 ARTICLES_PER_SOURCE 件まで取得する。
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from time import mktime

import feedparser
import yaml

from news_digest.settings import ARTICLES_PER_SOURCE, SOURCES_YAML
from news_digest.time_jst import JST

# RSS の summary に含まれる HTML タグをざっくり除去する
_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)


def _strip_html(text: str | None) -> str:
    """HTML タグを除き、連続空白を1つにまとめる。"""
    if not text:
        return ""
    plain = _TAG_RE.sub(" ", text)
    return " ".join(plain.split()).strip()


def _published_iso(entry: dict) -> str | None:
    """
    記事の公開日時を ISO8601（JST オフセット付き）にそろえる。

    FeedParser が提供する published_parsed（UTC基準として扱う）を優先する。
    無い場合は None。
    """
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    dt_utc = datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
    return dt_utc.astimezone(JST).isoformat()


def load_sources_yaml(path: Path | None = None) -> list[dict]:
    """sources.yaml を読み、sources リストを返す。"""
    p = path or SOURCES_YAML
    with p.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    sources = data.get("sources") or []
    return [s for s in sources if isinstance(s, dict) and s.get("url")]


def fetch_articles_from_rss(limit_per_source: int | None = None) -> list[dict]:
    """
    設定された全ソースから記事 dict のリストを返す。

    各 dict は Web テンプレート／将来の Gemini 入力と共通のキーにそろえる:
      title, link, source, published, summary, terms

    この段階では summary は RSS の要約またはタイトルのみ、terms は空リスト。
    """
    max_n = limit_per_source if limit_per_source is not None else ARTICLES_PER_SOURCE
    articles: list[dict] = []

    for src in load_sources_yaml():
        name = src.get("name") or src.get("id") or "unknown"
        url = src["url"]
        # parse: URL から直接取得（User-Agent が無いフィードがあるため明示）
        feed = feedparser.parse(
            url,
            agent="news-digest/0.2 (+local RSS reader)",
        )
        entries = getattr(feed, "entries", []) or []

        count = 0
        for entry in entries:
            if count >= max_n:
                break
            title = entry.get("title") or "(無題)"
            link = entry.get("link") or ""
            summary_raw = (
                entry.get("summary") or entry.get("description") or entry.get("title") or ""
            )
            summary = _strip_html(summary_raw)

            articles.append(
                {
                    "title": _strip_html(title),
                    "link": link,
                    "source": str(name),
                    "published": _published_iso(entry),
                    "summary": summary or title,
                    "terms": [],  # Step 3（Gemini）で埋める予定
                }
            )
            count += 1

    return articles
