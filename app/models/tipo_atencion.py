"""Tipo de atención seleccionado para el proceso (determina las reglas de validación)."""
from __future__ import annotations

from enum import Enum


class TipoAtencion(str, Enum):
    CONSULTA_EXTERNA = "Consulta Externa"
    URGENCIAS = "Urgencias"
