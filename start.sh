#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================="
echo "               SpotVault Launcher (Linux)              "
echo "======================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.11+: sudo apt install python3 python3-venv python3-tk ffmpeg"
    exit 1
fi

# 1. Virtual Environment Bootstrap (PEP 668 compliance for Debian 12 / Ubuntu 23.04+)
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    python3 -m venv "$VENV_DIR" 2>/dev/null || {
        echo "[ERROR] Failed to create virtual environment."
        echo "On Debian/Ubuntu systems, please run: sudo apt install python3-venv"
        exit 1
    }
fi

# 2. Activate virtual environment
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# 3. Verify Python packages inside .venv
if ! python -c "import spotdl, yt_dlp, mutagen, requests" &> /dev/null; then
    echo "[INFO] Installing required dependencies inside virtual environment..."
    pip install -r requirements.txt || {
        echo "[ERROR] Failed to install requirements."
        exit 1
    }
fi

# 4. Check GUI dependency (tkinter) if launching in GUI mode (no CLI arguments or --gui flag)
IS_CLI=0
for arg in "$@"; do
    case "$arg" in
        --cli|--url|--file|--sync-adb|--generate-playlists|--version|-h|--help)
            IS_CLI=1
            ;;
    esac
done

if [ "$IS_CLI" -eq 0 ]; then
    if ! python -c "import tkinter" &> /dev/null; then
        echo "[WARN] Tkinter is not installed on this system. GUI mode cannot launch."
        echo "To enable GUI: sudo apt install python3-tk"
        echo "Alternatively, you can run in CLI mode: ./start.sh --cli --file playlists.txt"
        exit 1
    fi
fi

# 5. Check FFmpeg availability
if ! command -v ffmpeg &> /dev/null && [ ! -f "core/ffmpeg" ] && [ ! -f "$HOME/.spotdl/ffmpeg" ]; then
    echo "[WARN] FFmpeg was not detected in PATH or ~/.spotdl."
    echo "Audio conversion may require FFmpeg: sudo apt install ffmpeg (or run: spotdl --download-ffmpeg)"
fi

echo "[LAUNCH] Starting SpotVault..."
python spotvault.py "$@"
