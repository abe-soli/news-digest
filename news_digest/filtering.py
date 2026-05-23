"""RSS記事の簡易フィルタリング。"""

from __future__ import annotations

from pathlib import Path

import yaml

from news_digest.settings import FILTER_RULES_YAML


def load_filter_rules(path: Path | None = None) -> dict:
    """filter_rules.yaml を読み込む。"""
    p = path or FILTER_RULES_YAML
    if not p.is_file():
        return {"exclude_keywords": []}
    with p.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {"exclude_keywords": []}


def filter_articles(articles: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    記事をフィルタリングし、(採用記事, 除外記事) を返す。

    除外記事には _filter_reason を付与する。
    """
    rules = load_filter_rules()
    keywords = [str(k) for k in (rules.get("exclude_keywords") or []) if str(k).strip()]

    kept: list[dict] = []
    rejected: list[dict] = []
    for article in articles:
        title = str(article.get("title") or "")
        summary = str(article.get("summary") or "")
        haystack = f"{title}\n{summary}".lower()

        matched = next((k for k in keywords if k.lower() in haystack), None)
        if matched:
            rejected.append({**article, "_filter_reason": f"keyword:{matched}"})
            continue
        kept.append(article)

    return kept, rejected
