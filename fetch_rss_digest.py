"""
手動実行用: RSS取得 → フィルタ → Gemini要約 → JSON保存。

バッチ（ログ付き）実行は run_batch.py を使ってください。

使い方:
  cd プロジェクトのルート
  python fetch_rss_digest.py
"""

from __future__ import annotations

from news_digest.pipeline import run_digest_pipeline


def main() -> int:
    result = run_digest_pipeline()
    if not result.success:
        print(f"エラー: {result.error_message or '不明'}")
        return 1

    print(f"保存しました: {result.saved_path}")
    print(
        f"記事数: 取得 {result.raw_count} -> 採用 {result.adopted_count} "
        f"(除外 {result.rejected_count}) / 削除した過去ファイル: {result.removed_old}"
    )
    if result.gemini_failures:
        print(f"Gemini要約失敗: {result.gemini_failures} 件（RSS要約のまま保存）")
    if result.rejected_samples:
        print("除外理由サンプル:")
        for reason, title in result.rejected_samples[:5]:
            print(f"- {reason}: {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
