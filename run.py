"""
Webサーバー起動用スクリプト。

使い方:
  python run.py
"""

from news_digest.web.app import create_app

app = create_app()

if __name__ == "__main__":
    # Render対応: 0.0.0.0で待ち受け、PORT環境変数を使用
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
