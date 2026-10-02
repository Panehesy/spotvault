@echo off
chcp 65001 >nul
title SpotVault - Spotify Playlist Archiver
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0core\run.ps1"
echo.
pause
