"""Acceso a los datos de soportes en SQL Server.

Las consultas usan siempre parámetros (`?`) para evitar SQL Injection.
"""
from __future__ import annotations

from app.services.database.connection import SqlServerConnection


class SoporteRepository:
    """Repositorio con la información necesaria para el renombramiento de soportes.

    TODO: reemplazar `obtener_soportes_pendientes` por la consulta real una vez
    definidas las tablas/columnas de origen junto con el usuario.
    """

    def __init__(self, conexion: SqlServerConnection | None = None) -> None:
        self._conexion = conexion or SqlServerConnection()

    def obtener_soportes_pendientes(self) -> list[dict]:
        consulta = "SELECT TOP (0) 1 AS placeholder"  # pendiente de definir con el usuario
        with self._conexion.obtener_cursor() as cursor:
            cursor.execute(consulta)
            columnas = [d[0] for d in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
