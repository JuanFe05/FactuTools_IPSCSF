"""Jerarquía de excepciones propias de la aplicación."""


class AppError(Exception):
    """Error base de la aplicación."""


class ConfigError(AppError):
    """Variables de entorno faltantes o inválidas."""


class DatabaseError(AppError):
    """Error al conectar o consultar SQL Server.

    El mensaje nunca debe incluir cadenas de conexión ni credenciales.
    """
