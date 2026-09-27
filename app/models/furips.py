"""Modelos relacionados con la separación de archivos FURIPS por número de factura."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FuripsFile:
    """Representa un archivo FURIPS encontrado en la carpeta principal."""

    path: Path
    prefix: str  # "furips1" o "furips2"


@dataclass(frozen=True)
class FuripsRecord:
    """Una línea de un archivo FURIPS junto con el ID de carpeta (número de factura) extraído."""

    folder_id: str
    raw_line: str


@dataclass
class SplitTask:
    """Agrupa las líneas que deben escribirse en un único archivo de salida."""

    folder_id: str
    output_prefix: str  # "FURIPS1" o "FURIPS2"
    lines: list[str] = field(default_factory=list)

    @property
    def output_filename(self) -> str:
        return f"{self.output_prefix}_{self.folder_id}.txt"


@dataclass
class ResultadoFactura:
    """Resultado de la separación de una factura (fila de la tabla en QML)."""

    numero_factura: str
    furips1_generado: bool = False
    furips2_generado: bool = False
    carpeta_creada: bool = False
    separado_correctamente: bool = False
    error: str = ""

    def a_diccionario(self) -> dict:
        """Representación plana usada por el modelo de tabla en QML."""
        return {
            "numeroFactura": self.numero_factura,
            "furips1": SplitTask(self.numero_factura, "FURIPS1").output_filename if self.furips1_generado else "—",
            "furips2": SplitTask(self.numero_factura, "FURIPS2").output_filename if self.furips2_generado else "—",
            "separado": self.separado_correctamente,
            "error": self.error,
        }


@dataclass
class ResultadoSeparacion:
    """Resumen agregado de un proceso de separación de archivos FURIPS."""

    total_txt_encontrados: int = 0
    carpetas_a_crear: int = 0
    carpetas_creadas: int = 0
    facturas: list[ResultadoFactura] = field(default_factory=list)

    @property
    def facturas_con_error(self) -> int:
        return sum(1 for f in self.facturas if f.error)

    def a_resumen(self) -> dict:
        return {
            "totalTxt": self.total_txt_encontrados,
            "carpetasACrear": self.carpetas_a_crear,
            "carpetasCreadas": self.carpetas_creadas,
            "facturasConError": self.facturas_con_error,
        }
