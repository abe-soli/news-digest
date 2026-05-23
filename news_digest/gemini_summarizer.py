"""Gemini Structured Outputs で summary / terms を生成する。"""

from __future__ import annotations

import logging
import time
from typing import Any

from google import genai
from pydantic import BaseModel, Field

from news_digest.settings import (
    GEMINI_API_KEY,
    GEMINI_DELAY_SECONDS,
    GEMINI_MAX_RETRIES,
    GEMINI_MODEL,
)


class TermItem(BaseModel):
    """用語と説明。"""

    term: str = Field(description="ニュース理解に役立つ重要語")
    definition: str = Field(description="中学生にも分かる短い説明")


class ArticleSummaryResult(BaseModel):
    """記事1件ぶんの要約結果。"""

    summary: str = Field(description="日本語で2-4文の要約")
    terms: list[TermItem] = Field(description="重要語の一覧（0-5件）")


def _build_prompt(article: dict[str, Any]) -> str:
    """記事要約用のプロンプトを作る。"""
    title = str(article.get("title") or "")
    source = str(article.get("source") or "")
    published = str(article.get("published") or "")
    body = str(article.get("summary") or "")
    return f"""
次のITニュース記事を日本語で要約してください。
返答は schema に従ってください。

[記事情報]
タイトル: {title}
媒体: {source}
公開日時: {published}
本文(抜粋): {body}

[要件]
- summary: 2-4文で、事実ベースで簡潔に
- terms: 理解に重要な専門語を0-5件
- 不確かな内容は断定しない
""".strip()


def _summarize_one(client: genai.Client, article: dict[str, Any]) -> ArticleSummaryResult:
    """1記事を要約（429/503 時は待機してリトライ）。"""
    last_exc: Exception | None = None
    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=_build_prompt(article),
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ArticleSummaryResult,
                    "temperature": 0.2,
                },
            )
            parsed = response.parsed
            if isinstance(parsed, ArticleSummaryResult):
                return parsed
            return ArticleSummaryResult.model_validate(parsed)
        except Exception as exc:
            last_exc = exc
            msg = str(exc).lower()
            retryable = "429" in msg or "503" in msg or "quota" in msg or "unavailable" in msg
            if not retryable or attempt >= GEMINI_MAX_RETRIES:
                raise
            wait = GEMINI_DELAY_SECONDS * attempt
            logging.getLogger(__name__).info(
                "Gemini リトライ (%d/%d) %d秒待機: %s",
                attempt,
                GEMINI_MAX_RETRIES,
                int(wait),
                exc,
            )
            time.sleep(wait)
    raise last_exc  # type: ignore[misc]


def enrich_articles_with_gemini(articles: list[dict]) -> tuple[list[dict], int]:
    """
    記事ごとに Gemini で summary / terms を生成して返す。

    APIキー未設定時は入力をそのまま返す。

    Returns:
        (要約済み記事リスト, Gemini失敗件数)
    """
    if not GEMINI_API_KEY:
        return articles, 0

    client = genai.Client(api_key=GEMINI_API_KEY)
    enriched: list[dict] = []
    failures = 0
    for i, article in enumerate(articles):
        if i > 0 and GEMINI_DELAY_SECONDS > 0:
            time.sleep(GEMINI_DELAY_SECONDS)
        try:
            result = _summarize_one(client, article)
            payload = result.model_dump()
            enriched.append(
                {
                    **article,
                    "summary": payload["summary"],
                    "terms": payload["terms"],
                }
            )
        except Exception as exc:
            # API失敗時はRSS由来の summary を維持して処理継続する
            failures += 1
            title = str(article.get("title") or "(無題)")
            logging.getLogger(__name__).warning(
                "Gemini 要約失敗 (%s): %s", title[:60], exc
            )
            enriched.append({**article, "terms": article.get("terms") or []})

    return enriched, failures
