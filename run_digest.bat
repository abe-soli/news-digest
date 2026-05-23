@echo off
REM 毎朝6時など、Windowsタスクスケジューラから実行する用バッチ
REM 下の cd パスを自分の news-digest フォルダに合わせてください

cd /d "C:\dev\news-digest"
python run_batch.py
exit /b %ERRORLEVEL%
