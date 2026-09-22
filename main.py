"""Punto de entrada de Rename APP."""
from __future__ import annotations

import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from app.config.logging_config import configure_logging
from app.config.paths import resource_path
from app.config.settings import AppConfig
from app.controllers.app_controller import AppController
from app.controllers.renombrar_controller import RenombrarController

_QML_DIR = resource_path("app", "views", "qml")


def main() -> int:
    config = AppConfig()
    configure_logging(config.log_level, config.app_name)

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(sys.argv)
    app.setOrganizationName(config.org_name)
    app.setApplicationName(config.app_name)
    app.setApplicationVersion(config.app_version)

    engine = QQmlApplicationEngine()
    controlador = AppController()
    renombrar_controlador = RenombrarController()
    engine.rootContext().setContextProperty("AppCtl", controlador)
    engine.rootContext().setContextProperty("RenombrarCtl", renombrar_controlador)

    engine.addImportPath(str(_QML_DIR))
    engine.load(QUrl.fromLocalFile(str(_QML_DIR / "main.qml")))
    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
