"""Parseo de archivos FURIPS1/FURIPS2 para extraer el ID de carpeta (número de factura)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.models.furips import FuripsRecord

_ENCODING_PRIMARY = "utf-8"
_ENCODING_FALLBACK = "latin-1"


def _read_lines(path: Path) -> list[str]:
    """Lee las líneas de un archivo intentando UTF-8 y luego latin-1."""
    for encoding in (_ENCODING_PRIMARY, _ENCODING_FALLBACK):
        try:
            return path.read_text(encoding=encoding).splitlines()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo leer '{path.name}' con ninguna codificación soportada.")


# ---------------------------------------------------------------------------
# Estrategia abstracta
# ---------------------------------------------------------------------------


class FuripsParser(ABC):
    """Define el contrato para parsear un archivo FURIPS y extraer registros."""

    @property
    @abstractmethod
    def output_prefix(self) -> str:
        """Prefijo del archivo de salida (ej. 'FURIPS1')."""

    @abstractmethod
    def _extract_id(self, line: str) -> str | None:
        """Extrae el ID de carpeta de una línea; retorna None si la línea es inválida."""

    def parse(self, path: Path) -> list[FuripsRecord]:
        """Lee el archivo y devuelve la lista de registros válidos."""
        records: list[FuripsRecord] = []
        for raw_line in _read_lines(path):
            if not raw_line.strip():
                continue
            folder_id = self._extract_id(raw_line)
            if folder_id:
                records.append(FuripsRecord(folder_id=folder_id, raw_line=raw_line))
        return records


# ---------------------------------------------------------------------------
# Estrategias concretas
# ---------------------------------------------------------------------------


class Furips1Parser(FuripsParser):
    """
    Parsea archivos FURIPS1.

    Formato de línea: ``,,FE01283347,8902,...``
    El ID de carpeta se encuentra en el índice 2 tras separar por coma.
    """

    @property
    def output_prefix(self) -> str:
        return "FURIPS1"

    def _extract_id(self, line: str) -> str | None:
        parts = line.split(",")
        if len(parts) > 2:
            folder_id = parts[2].strip()
            return folder_id or None
        return None


class Furips2Parser(FuripsParser):
    """
    Parsea archivos FURIPS2.

    Formato de línea: ``FE01283347,8902,...``
    El ID de carpeta se encuentra en el índice 0 tras separar por coma.
    """

    @property
    def output_prefix(self) -> str:
        return "FURIPS2"

    def _extract_id(self, line: str) -> str | None:
        parts = line.split(",")
        if parts:
            folder_id = parts[0].strip()
            return folder_id or None
        return None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class FuripsParserFactory:
    """Crea el parser adecuado según el prefijo del archivo FURIPS."""

    _registry: dict[str, FuripsParser] = {
        "furips1": Furips1Parser(),
        "furips2": Furips2Parser(),
    }

    @classmethod
    def create(cls, prefix: str) -> FuripsParser:
        parser = cls._registry.get(prefix.lower())
        if parser is None:
            raise ValueError(f"Prefijo desconocido: '{prefix}'. Se esperaba 'furips1' o 'furips2'.")
        return parser
