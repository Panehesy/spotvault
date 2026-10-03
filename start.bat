@echo off
chcp 65001 >nul
title SpotVault v1.0.1 Launcher
cd /d "%~dp0"

echo =======================================================
echo              SpotVault v1.0.1 - Baslatici
echo =======================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python sisteminizde bulunamadi!
    echo Lutfen https://www.python.org adresinden Python 3.11+ yukleyin
    echo ve 'Add Python to PATH' kutusunu isaretleyin.
    pause
    exit /b 1
)

python -c "import yt_dlp, mutagen, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [BILGI] Gerekli paketler yukleniyor...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [HATA] Paketler yuklenirken bir sorun olustu.
        pause
        exit /b 1
    )
)

echo [BASLATILIYOR] SpotVault calistiriliyor...
python spotvault.py %*

if %errorlevel% neq 0 (
    echo.
    echo SpotVault bir hata ile sonlandi.
    pause
)
