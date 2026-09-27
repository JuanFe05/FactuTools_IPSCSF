"""Gestión de la conexión a SQL Server mediante un context manager."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

import pyodbc

from app.config.settings import AppConfig
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class SqlServerConnection:
    """Crea conexiones pyodbc a partir de la configuración de la app."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or AppConfig()

    @contextmanager
    def obtener_cursor(self) -> Iterator[pyodbc.Cursor]:
        """Entrega un cursor listo para usar; hace commit/rollback y cierra la conexión."""
        conexion: pyodbc.Connection | None = None
        try:
            conexion = pyodbc.connect(self._config.database.connection_string(), timeout=10)
            cursor = conexion.cursor()
            yield cursor
            conexion.commit()
        except pyodbc.Error:
            if conexion is not None:
                conexion.rollback()
            logger.exception("Error de conexión/consulta a SQL Server")
            raise DatabaseError("No fue posible completar la operación con la base de datos.") from None
        finally:
            if conexion is not None:
                conexion.close()
