"""Escaneo de la carpeta principal: detecta archivos FURIPS1 y FURIPS2."""
from __future__ import annotations

from pathlib import Path

from app.models.furips import FuripsFile

_FURIPS_PREFIXES = ("furips1", "furips2")


class FuripsFileScanner:
    """Busca los archivos FURIPS1 y FURIPS2 dentro de la carpeta seleccionada."""

    def scan(self, folder: Path) -> list[FuripsFile]:
        if not folder.is_dir():
            return []

        found: list[FuripsFile] = []
        for path in folder.iterdir():
            if not path.is_file():
                continue
            lower_stem = path.stem.lower()
            for prefix in _FURIPS_PREFIXES:
                if lower_stem.startswith(prefix):
                    found.append(FuripsFile(path=path, prefix=prefix))
                    break
        return sorted(found, key=lambda f: f.prefix)
