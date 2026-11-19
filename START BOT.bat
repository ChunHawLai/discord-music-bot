@echo off
cd /d "%~dp0"
title Discord Music Bot
echo ============================================
echo   Discord Music Bot - Starting...
echo ============================================
echo.
echo Keep this window open while the bot is running.
echo Press Ctrl+C to stop the bot.
echo.
.\.venv\Scripts\python.exe bot.py
echo.
echo Bot has stopped. (If you didn't stop it, check the error above.)
pause
