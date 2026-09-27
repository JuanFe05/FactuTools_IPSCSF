"""Consulta el último release de GitHub y compara versiones (SemVer)."""
from __future__ import annotations

import logging

import requests
from packaging.version import InvalidVersion, Version

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"


class UpdateChecker:
    """Determina si existe una versión más nueva publicada en GitHub Releases."""

    def __init__(self, repo: str, version_actual: str) -> None:
        self._repo = repo
        self._version_actual = version_actual

    def buscar_actualizacion(self) -> dict | None:
        """Retorna {"version", "notas", "url_descarga"} si hay una versión nueva, si no None."""
        if not self._repo:
            return None
        try:
            respuesta = requests.get(_GITHUB_API.format(repo=self._repo), timeout=8)
            respuesta.raise_for_status()
        except requests.RequestException:
            logger.warning("No se pudo verificar actualizaciones", exc_info=True)
            return None

        datos = respuesta.json()
        tag = str(datos.get("tag_name", "")).lstrip("v")
        try:
            if Version(tag) <= Version(self._version_actual):
                return None
        except InvalidVersion:
            logger.warning("Tag de versión inválido recibido de GitHub: %s", tag)
            return None

        activo_instalador = next(
            (a for a in datos.get("assets", []) if a.get("name", "").lower().endswith(".exe")),
            None,
        )
        return {
            "version": tag,
            "notas": datos.get("body", ""),
            "url_descarga": activo_instalador["browser_download_url"] if activo_instalador else None,
        }
