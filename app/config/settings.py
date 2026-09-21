"""Configuración centralizada de la app, cargada desde variables de entorno (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BASE_DIR / ".env")


def _env(clave: str, default: str = "") -> str:
    return os.getenv(clave, default)


def _env_bool(clave: str, default: bool = False) -> bool:
    valor = os.getenv(clave)
    if valor is None:
        return default
    return valor.strip().lower() in {"1", "true", "yes", "si"}


@dataclass(frozen=True)
class DatabaseSettings:
    """Parámetros de conexión a Microsoft SQL Server."""

    server: str
    port: int
    database: str
    user: str
    password: str
    driver: str
    encrypt: bool
    trust_server_certificate: bool

    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};PWD={self.password};"
            f"Encrypt={'yes' if self.encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'};"
        )


class AppConfig:
    """Configuración global de la aplicación (Singleton)."""

    _instancia: "AppConfig | None" = None

    def __new__(cls) -> "AppConfig":
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        self.app_name = _env("APP_NAME", "FactuTools App")
        self.app_version = _env("APP_VERSION", "0.1.0")
        self.org_name = _env("ORG_NAME", "IPS Clínica Salud Florida")
        self.clinic_name = _env("CLINIC_NAME", "IPS Clínica Salud Florida")
        self.environment = _env("APP_ENV", "development")
        self.log_level = _env("LOG_LEVEL", "INFO")
        self.github_repo = _env("GITHUB_REPO", "")  # formato "owner/repo"

        self.database = DatabaseSettings(
            server=_env("DB_SERVER"),
            port=int(_env("DB_PORT", "1433") or 1433),
            database=_env("DB_NAME"),
            user=_env("DB_USER"),
            password=_env("DB_PASSWORD"),
            driver=_env("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            encrypt=_env_bool("DB_ENCRYPT", True),
            trust_server_certificate=_env_bool("DB_TRUST_SERVER_CERTIFICATE", False),
        )
