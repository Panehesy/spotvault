@echo off
chcp 65001 >nul
title SpotVault Launcher
cd /d "%~dp0"

echo =======================================================
echo              SpotVault - Baslatici
echo =======================================================

set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    py -3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py -3
    )
)

if "%PYTHON_CMD%"=="" (
    echo [HATA] Python sisteminizde bulunamadi!
    echo Lutfen https://www.python.org adresinden Python 3.11+ yukleyin
    echo ve 'Add Python to PATH' kutusunu isaretleyin.
    if "%~1"=="" pause
    exit /b 1
)

%PYTHON_CMD% -c "import spotdl, yt_dlp, mutagen, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [BILGI] Gerekli paketler yukleniyor...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [HATA] Paketler yuklenirken bir sorun olustu.
        if "%~1"=="" pause
        exit /b 1
    )
)

echo [BASLATILIYOR] SpotVault calistiriliyor...
%PYTHON_CMD% spotvault.py %*
set APP_EXIT=%errorlevel%

if %APP_EXIT% neq 0 (
    echo.
    echo [UYARI] SpotVault cikis kodu: %APP_EXIT%
    if "%~1"=="" pause
    exit /b %APP_EXIT%
)
