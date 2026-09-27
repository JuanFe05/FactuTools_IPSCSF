"""Contrato que debe cumplir cada empresa para validar y renombrar sus soportes."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.models.factura_info import FacturaInfo
from app.models.subcarpeta import ContextoRenombrado, ResultadoValidacion
from app.models.tipo_atencion import TipoAtencion


class ValidadorSoportes(Protocol):
    """Estrategia de validación/renombrado específica de una empresa."""

    def extraer_identificador(self, nombre_carpeta: str) -> str | None:
        """Obtiene el identificador (ej. número de admisión) desde el nombre de la subcarpeta."""
        ...

    def validar(
        self, pdfs: list[Path], tipo_atencion: TipoAtencion, factura: FacturaInfo | None
    ) -> ResultadoValidacion:
        """Determina si los PDFs de una subcarpeta cumplen los soportes obligatorios."""
        ...

    def nombre_nuevo_archivo(self, pdf: Path, contexto: ContextoRenombrado) -> str:
        """Calcula el nuevo nombre (con extensión) para un PDF."""
        ...

    def nombre_nueva_carpeta(self, contexto: ContextoRenombrado) -> str:
        """Calcula el nuevo nombre para la subcarpeta."""
        ...
