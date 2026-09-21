"""Resolución de rutas de recursos (funciona en desarrollo y en un ejecutable empaquetado)."""
from __future__ import annotations

import sys
from pathlib import Path

# En desarrollo, la raíz del proyecto. En un ejecutable PyInstaller, sys._MEIPASS apunta a
# la carpeta temporal donde se extraen los datos empaquetados (ver --add-data al generar el .exe).
_BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent.parent))


def resource_path(*partes: str) -> Path:
    return _BASE_DIR.joinpath(*partes)
