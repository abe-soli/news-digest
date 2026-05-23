# AIニュースダイジェスト

毎朝のITニュースをRSSで取得し、Geminiで要約してブラウザで閲覧するアプリです。

## 必要なもの

- Python 3.11 以上（`zoneinfo` 利用のため）
- インターネット接続（パッケージのインストール・将来のRSS取得用）

## セットアップ（仮想環境なし）

プロジェクトフォルダで、**そのまま** pip で依存関係を入れます。

```powershell
cd "c:\Users\solil\OneDrive\ドキュメント\news-digest"
python -m pip install -r requirements.txt
```

`pip` コマンドが見つからない場合は、上のように `python -m pip` を使ってください（仮想環境は使いません）。

> **注意**: グローバル（ユーザー環境）にパッケージが入ります。他のPythonプロジェクトとバージョンがぶつかる場合は、そのときだけ venv の利用を検討してください。

## RSS だけでダイジェストを作る（Step 2）

依存関係に `feedparser` を追加済みです。未取得ならインストールし直してください。

```powershell
python -m pip install -r requirements.txt
python fetch_rss_digest.py
```

`data/digest-YYYY-MM-DD.json` ができたら、その日付の実データが Web に表示されます（要約本文はフィード由来・用語欄は空のまま）。

## Gemini要約付きでダイジェストを作る（Step 3）

`.env` に APIキーを設定すると、`fetch_rss_digest.py` 実行時に
Gemini Structured Outputs で `summary` と `terms` を生成します。

```powershell
copy .env.example .env
# .env を開いて GEMINI_API_KEY を設定
python fetch_rss_digest.py
```

記事フィルタは `config/filter_rules.yaml` の `exclude_keywords` で調整できます。

## 毎朝の自動実行（Step 4）

手動と同じ処理を、**ログ付き**で実行するエントリポイントです。

```powershell
python run_batch.py
```

- ログは `logs/run-YYYY-MM-DD_HHMMSS.log` に1実行1ファイルで保存されます
- 成功・失敗・除外件数・Gemini失敗件数が記録されます
- 終了コード: 成功 `0` / 失敗 `1`（タスクスケジューラの「前回の実行結果」に反映）

### Windows タスクスケジューラの設定例

1. `run_digest.bat` を開き、`cd /d` のパスを自分のフォルダに合わせる（例: `C:\dev\news-digest`）
2. **タスクスケジューラ** → **基本タスクの作成**
3. トリガー: 毎日 **午前6:00**
4. 操作: **プログラムの開始**
   - プログラム/スクリプト: `C:\dev\news-digest\run_digest.bat`（フルパス）
   - 開始（オプション）: `C:\dev\news-digest`
5. 保存後、右クリック → **実行** でテスト
6. `logs/` に新しい `.log` ができ、中身に `バッチ成功` があればOK

> `python` が見つからない場合は、バッチ内を `py -3 run_batch.py` や Python のフルパスに変更してください。

## Webサーバーの起動（Step 1）

```powershell
python run.py
```

ブラウザで次を開きます。

- 今日のダイジェスト: http://127.0.0.1:5000/
- 過去一覧: http://127.0.0.1:5000/archive

本日分の `data/digest-YYYY-MM-DD.json` が無い場合は、`data/sample-digest.json` のサンプルが表示されます。

## 環境変数（Step 3 以降）

要約機能を使うときに `.env` を作成します。

```powershell
copy .env.example .env
```

`.env` に `GEMINI_API_KEY` を設定してください。

無料枠は **1分あたりのリクエスト数に上限** があります。記事数が多いときは `.env` の `GEMINI_DELAY_SECONDS=13`（既定）で間隔を空けてください。

## フォルダ構成（概要）

| パス | 説明 |
|------|------|
| `config/sources.yaml` | RSSソース一覧 |
| `data/` | 日付ごとのダイジェスト JSON |
| `logs/` | バッチ実行ログ（`run-*.log`） |
| `news_digest/` | Python パッケージ |
| `fetch_rss_digest.py` | 手動実行（コンソール出力のみ） |
| `run_batch.py` | 自動実行用（ログ付き・タスクスケジューラ向け） |
| `run_digest.bat` | タスクスケジューラから呼ぶバッチファイル |
| `config/filter_rules.yaml` | レビュー・セール系記事の除外ルール |

## 開発の進捗

- [x] Step 1: Flask + ダミー（サンプル）データ表示
- [x] Step 2: RSS 取得（`fetch_rss_digest.py`・JSON 保存・90日超の削除）
- [x] Step 3: Gemini 要約（Structured Outputs）+ 記事フィルタ
- [x] Step 4: タスク連携・ログ（`run_batch.py` / `run_digest.bat`）
- [ ] Step 5: 読み上げ・仕上げ
