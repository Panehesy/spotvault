"""
Visual styling tokens and color palettes for SpotVault Desktop Dark Theme.
"""

BG_MAIN = "#0b1329"
BG_SURFACE = "#152238"
BG_CARD = "#1c2d4a"
BG_INPUT = "#0f172a"

BORDER_COLOR = "#2a3e5c"
BORDER_FOCUS = "#38bdf8"

ACCENT_PRIMARY = "#10b981"
ACCENT_HOVER = "#059669"
ACCENT_SPOTIFY = "#1db954"

TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

STATUS_SUCCESS = "#10b981"
STATUS_WARNING = "#f59e0b"
STATUS_ERROR = "#ef4444"

import sys

if sys.platform.startswith("win"):
    FONT_FAMILY = "Segoe UI"
    FONT_CONSOLE_FAMILY = "Consolas"
elif sys.platform.startswith("darwin"):
    FONT_FAMILY = "SF Pro Display"
    FONT_CONSOLE_FAMILY = "Menlo"
else:
    FONT_FAMILY = "DejaVu Sans"
    FONT_CONSOLE_FAMILY = "DejaVu Sans Mono"

FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_HEADING = (FONT_FAMILY, 10, "bold")
FONT_BODY = (FONT_FAMILY, 9)
FONT_CONSOLE = (FONT_CONSOLE_FAMILY, 9)
