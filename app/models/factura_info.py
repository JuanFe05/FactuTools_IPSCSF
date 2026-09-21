"""Información de factura obtenida desde SQL Server."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FacturaInfo:
    numero_factura: str
    empresa: str
    fecha_facturacion: str
    estado: str
    usuario_factura: str
    relacion_envio: str
    nit: str = ""
    total: int = 0
