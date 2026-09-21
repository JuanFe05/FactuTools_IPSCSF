"""Estados posibles del proceso de renombramiento de una subcarpeta."""
from __future__ import annotations

from enum import Enum


class EstadoRenombramiento(str, Enum):
    PENDIENTE = "Pendiente"
    PROCESANDO = "Procesando"
    COMPLETADO = "Completado"
    ERROR = "Error"
