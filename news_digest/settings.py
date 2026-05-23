"""プロジェクト全体の設定（パス・環境変数）。"""

import os
from pathlib import Path

from dotenv import load_dotenv

# リポジトリのルート（news_digest のひとつ上）
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# .env を読み込む（存在しなくてもエラーにしない）
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"
SOURCES_YAML = CONFIG_DIR / "sources.yaml"
FILTER_RULES_YAML = CONFIG_DIR / "filter_rules.yaml"

# 1ソースあたり取得する記事数（RSS・要約バッチで使用予定）
ARTICLES_PER_SOURCE = 10

# ダイジェストJSONの保持日数
RETENTION_DAYS = 90

# Gemini 設定（Step 3）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# 無料枠はモデルごとに「分あたり5リクエスト」程度の制限があるため、記事間で待機する（秒）
GEMINI_DELAY_SECONDS = float(os.getenv("GEMINI_DELAY_SECONDS", "13"))
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
