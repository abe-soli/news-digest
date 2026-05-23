@echo off
cd /d C:\dev\news-digest

echo [%date% %time%] RSS fetch started...
python fetch_rss_digest.py

if %errorlevel% neq 0 (
    echo [%date% %time%] RSS fetch failed!
    exit /b 1
)

echo [%date% %time%] Git add...
git add .

echo [%date% %time%] Git commit...
git commit -m "daily update"

if %errorlevel% neq 0 (
    echo [%date% %time%] Nothing to commit or commit failed
    exit /b 0
)

echo [%date% %time%] Git push...
git push

if %errorlevel% neq 0 (
    echo [%date% %time%] Git push failed!
    exit /b 1
)

echo [%date% %time%] Deployment completed successfully!
