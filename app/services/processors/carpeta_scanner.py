"""Escaneo de la carpeta principal: detecta subcarpetas y sus archivos PDF."""
from __future__ import annotations

from pathlib import Path

from app.models.subcarpeta import SubcarpetaDetectada


def escanear_carpeta_principal(carpeta_principal: Path) -> list[SubcarpetaDetectada]:
    """Retorna cada subcarpeta directa de `carpeta_principal` junto con sus PDFs."""
    if not carpeta_principal.is_dir():
        return []

    subcarpetas: list[SubcarpetaDetectada] = []
    for ruta in sorted(p for p in carpeta_principal.iterdir() if p.is_dir()):
        pdfs = sorted(ruta.glob("*.pdf"))
        subcarpetas.append(SubcarpetaDetectada(nombre=ruta.name, ruta=ruta, pdfs=pdfs))
    return subcarpetas
