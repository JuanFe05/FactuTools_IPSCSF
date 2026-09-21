"""Modelos relacionados con las subcarpetas detectadas y el resultado de procesarlas."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.models.estado_renombramiento import EstadoRenombramiento
from app.models.factura_info import FacturaInfo


@dataclass
class SubcarpetaDetectada:
    """Subcarpeta encontrada dentro de la carpeta principal, con sus PDFs."""

    nombre: str
    ruta: Path
    pdfs: list[Path] = field(default_factory=list)


@dataclass
class ResultadoValidacion:
    """Resultado de aplicar las reglas de validación de una empresa a una subcarpeta."""

    es_correcto: bool
    detalles: list[str] = field(default_factory=list)


@dataclass
class ContextoRenombrado:
    """Datos disponibles para que un validador calcule los nuevos nombres."""

    subcarpeta: SubcarpetaDetectada
    factura: FacturaInfo | None
    empresa: str


@dataclass
class ResultadoSubcarpeta:
    """Resultado final (validación + renombramiento) de una subcarpeta procesada."""

    nombre_carpeta: str
    numero_factura: str
    registro_encontrado: bool
    archivos_correctos: bool | None
    empresa: str
    fecha_facturacion: str
    estado: str
    usuario_factura: str
    relacion_envio: str
    total: int
    estado_renombramiento: EstadoRenombramiento
    detalles_validacion: list[str] = field(default_factory=list)
    motivo_error: str = ""

    def a_diccionario(self) -> dict:
        """Representación plana usada por el modelo de tabla en QML."""
        return {
            "nombreCarpeta": self.nombre_carpeta,
            "numeroFactura": self.numero_factura if self.registro_encontrado else "—",
            "registroEncontrado": self.registro_encontrado,
            "archivosCorrectos": self.archivos_correctos,  # None = validación pendiente
            "empresa": self.empresa if self.registro_encontrado else "—",
            "fechaFacturacion": self.fecha_facturacion if self.registro_encontrado else "—",
            "estado": self.estado if self.registro_encontrado else "—",
            "usuarioFactura": self.usuario_factura if self.registro_encontrado else "—",
            "total": self.total if self.registro_encontrado else 0,
            "estadoRenombramiento": self.estado_renombramiento.value,
            "detallesValidacion": self.detalles_validacion,
            "motivoError": self.motivo_error,
        }


@dataclass
class ResultadoProceso:
    """Resumen agregado de un proceso de renombramiento completo."""

    total_pdfs: int = 0
    archivos_renombrados: int = 0
    carpetas_renombradas: int = 0
    subcarpetas: list[ResultadoSubcarpeta] = field(default_factory=list)

    @property
    def total_subcarpetas(self) -> int:
        return len(self.subcarpetas)

    @property
    def total_registros_encontrados(self) -> int:
        return sum(1 for s in self.subcarpetas if s.registro_encontrado)

    @property
    def total_registros_no_encontrados(self) -> int:
        return sum(1 for s in self.subcarpetas if not s.registro_encontrado)

    @property
    def total_con_error_renombrado(self) -> int:
        return sum(1 for s in self.subcarpetas if s.estado_renombramiento == EstadoRenombramiento.ERROR)

    def a_resumen(self) -> dict:
        return {
            "subcarpetas": self.total_subcarpetas,
            "archivos": self.total_pdfs,
            "registrosEncontrados": self.total_registros_encontrados,
            "registrosNoEncontrados": self.total_registros_no_encontrados,
            "subcarpetasConError": self.total_con_error_renombrado,
            "carpetasRenombradas": self.carpetas_renombradas,
            "archivosRenombrados": self.archivos_renombrados,
        }
