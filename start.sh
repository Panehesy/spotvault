#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================="
echo "           SpotVault v1.0.1 Launcher (Linux)           "
echo "======================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.11+: sudo apt install python3 python3-pip python3-tk"
    exit 1
fi

python3 -c "import yt_dlp, mutagen, requests" &> /dev/null || {
    echo "[INFO] Installing required dependencies..."
    pip3 install -r requirements.txt || pip install -r requirements.txt
}

echo "[LAUNCH] Starting SpotVault..."
python3 spotvault.py "$@"
