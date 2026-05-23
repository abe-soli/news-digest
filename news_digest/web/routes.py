"""Webページのルート定義。"""

from datetime import date

from flask import Blueprint, abort, render_template

from news_digest.storage import list_digest_dates, load_digest
from news_digest.time_jst import format_date, today_jst

bp = Blueprint("main", __name__)


def _collect_terms(articles: list[dict]) -> list[dict]:
    """全記事の用語をまとめる（右カラム用）。重複用語は先勝ち。"""
    seen: set[str] = set()
    terms: list[dict] = []
    for article in articles:
        for item in article.get("terms") or []:
            word = item.get("term", "")
            if word and word not in seen:
                seen.add(word)
                terms.append(item)
    return terms


@bp.route("/")
def index():
    """今日のダイジェスト（無ければサンプル）。"""
    digest, is_sample = load_digest()
    if digest is None:
        abort(404, description="ダイジェストが見つかりません。")

    articles = digest.get("articles") or []
    return render_template(
        "index.html",
        digest=digest,
        articles=articles,
        terms=_collect_terms(articles),
        is_sample=is_sample,
        page_title="今日のニュース",
    )


@bp.route("/digest/<date_str>")
def digest_by_date(date_str: str):
    """指定日のダイジェスト。"""
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        abort(404)

    digest, is_sample = load_digest(d)
    if digest is None:
        abort(404, description=f"{date_str} のダイジェストはありません。")

    articles = digest.get("articles") or []
    return render_template(
        "index.html",
        digest=digest,
        articles=articles,
        terms=_collect_terms(articles),
        is_sample=is_sample,
        page_title=f"{date_str} のニュース",
    )


@bp.route("/archive")
def archive():
    """過去のダイジェスト一覧。"""
    dates = list_digest_dates()
    today = format_date(today_jst())
    return render_template(
        "archive.html",
        dates=dates,
        today=today,
    )
