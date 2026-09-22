"""Configuración de validación/renombrado por empresa (datos, no código por empresa)."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.models.tipo_atencion import TipoAtencion


@dataclass(frozen=True)
class ReglaSoportes:
    """Prefijos de PDF exigidos para una combinación empresa + tipo de atención."""

    prefijos_obligatorios: tuple[str, ...]
    # Si se define, basta con que al menos uno de estos prefijos esté presente.
    grupo_alternativo: tuple[str, ...] = ()


@dataclass(frozen=True)
class EmpresaConfig:
    """Reglas de una empresa: por tipo de atención, prefijo de factura y nomenclatura de carpeta."""

    nombre: str
    reglas: dict[TipoAtencion, ReglaSoportes] = field(default_factory=dict)
    prefijo_factura: str = "FEV"
    carpeta_incluye_nit: bool = False
    nit_ips: str = "815000253"
    # Nombres adicionales tal como aparecen en la base de datos que deben aceptarse como la
    # misma empresa (ej. regímenes registrados con formato distinto al de los sufijos estándar).
    nombres_alternativos: tuple[str, ...] = ()
