@echo off
cd /d C:\dev\news-digest

set LOG_FILE=logs\auto_deploy-%date:~-10,4%-%date:~-5,2%-%date:~-2,2%.log

echo [%date% %time%] RSS fetch started... >> %LOG_FILE%
python fetch_rss_digest.py >> %LOG_FILE% 2>&1

if %errorlevel% neq 0 (
    echo [%date% %time%] RSS fetch failed! >> %LOG_FILE%
    exit /b 1
)

echo [%date% %time%] Git add... >> %LOG_FILE%
git add . >> %LOG_FILE% 2>&1

echo [%date% %time%] Git commit... >> %LOG_FILE%
git commit -m "daily update" >> %LOG_FILE% 2>&1

if %errorlevel% neq 0 (
    echo [%date% %time%] Nothing to commit or commit failed >> %LOG_FILE%
    exit /b 0
)

echo [%date% %time%] Git push... >> %LOG_FILE%
git push >> %LOG_FILE% 2>&1

if %errorlevel% neq 0 (
    echo [%date% %time%] Git push failed! >> %LOG_FILE%
    exit /b 1
)

echo [%date% %time%] Deployment completed successfully! >> %LOG_FILE%
