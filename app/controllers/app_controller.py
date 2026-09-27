"""Facade principal expuesto a QML: punto único de acceso a la app desde la UI."""
from __future__ import annotations

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.config.paths import resource_path
from app.config.settings import AppConfig
from app.services.update.update_checker import UpdateChecker


class AppController(QObject):
    """Expone datos generales de la app y coordina la verificación de actualizaciones."""

    actualizacionDisponible = Signal(str, str)  # version, url_descarga

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._config = AppConfig()
        self._update_checker = UpdateChecker(self._config.github_repo, self._config.app_version)

    @Property(str, constant=True)
    def appName(self) -> str:
        return self._config.app_name

    @Property(str, constant=True)
    def appVersion(self) -> str:
        return self._config.app_version

    @Property(str, constant=True)
    def clinicName(self) -> str:
        return self._config.clinic_name

    @Property(str, constant=True)
    def logoUrl(self) -> str:
        """URL del logo, resuelta de forma robusta (válida también en un ejecutable empaquetado)."""
        ruta = resource_path("app", "resources", "images", "Logo.png")
        return QUrl.fromLocalFile(str(ruta)).toString()

    @Slot()
    def verificarActualizaciones(self) -> None:
        info = self._update_checker.buscar_actualizacion()
        if info and info.get("url_descarga"):
            self.actualizacionDisponible.emit(info["version"], info["url_descarga"])
