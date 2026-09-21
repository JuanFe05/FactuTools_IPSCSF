"""Configuración del sistema de logging de la aplicación."""
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType


def _directorio_logs(nombre_app: str) -> Path:
    base = os.getenv("LOCALAPPDATA") or str(Path.home())
    directorio = Path(base) / nombre_app / "logs"
    directorio.mkdir(parents=True, exist_ok=True)
    return directorio


def configure_logging(nivel: str = "INFO", nombre_app: str = "FactuToolsApp") -> None:
    """Configura handlers de archivo (rotativo) y consola, y captura excepciones no manejadas."""
    logger = logging.getLogger()
    if logger.handlers:
        return  # ya configurado (evita duplicar handlers)
    logger.setLevel(nivel.upper())

    formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

    archivo = _directorio_logs(nombre_app) / "app.log"
    handler_archivo = RotatingFileHandler(archivo, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    handler_archivo.setFormatter(formato)
    logger.addHandler(handler_archivo)

    handler_consola = logging.StreamHandler()
    handler_consola.setFormatter(formato)
    logger.addHandler(handler_consola)

    def _capturar_excepcion_no_manejada(
        tipo: type[BaseException], valor: BaseException, tb: TracebackType | None
    ) -> None:
        if issubclass(tipo, KeyboardInterrupt):
            sys.__excepthook__(tipo, valor, tb)
            return
        logging.getLogger("excepcion_no_manejada").critical(
            "Error no controlado", exc_info=(tipo, valor, tb)
        )

    sys.excepthook = _capturar_excepcion_no_manejada
