"""Normalización de nombres de empresa (basada en la macro VBA de referencia).

La base de datos puede devolver el nombre de la empresa con sufijo de régimen
(" CONTRIBUTIVO", " SUBSIDIADO", " CONTRIBUTIVO & SUBSIDIADO"), mientras que el
formulario ofrece un nombre unificado. Ambos deben compararse por su "base".
"""
from __future__ import annotations

_SUFIJOS_REGIMEN = (" CONTRIBUTIVO & SUBSIDIADO", " CONTRIBUTIVO", " SUBSIDIADO")


def normalizar_nombre_empresa(nombre: str) -> str:
    base = (nombre or "").strip().upper()
    for sufijo in _SUFIJOS_REGIMEN:
        base = base.replace(sufijo, "")
    base = base.strip()
    if base.startswith("EPS SANITAS"):
        base = "EPS SANITAS"
    return base


def empresas_coinciden(nombre_en_datos: str, empresa_seleccionada: str) -> bool:
    return normalizar_nombre_empresa(nombre_en_datos) == normalizar_nombre_empresa(empresa_seleccionada)
