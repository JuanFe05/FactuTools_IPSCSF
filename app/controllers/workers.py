"""Workers (QThread) para ejecutar tareas largas sin bloquear la interfaz."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from app.models.furips import ResultadoSeparacion
from app.models.subcarpeta import ResultadoProceso
from app.models.tipo_atencion import TipoAtencion
from app.services.csv.factura_csv_source import FacturaCsvSource
from app.use_cases.procesar_renombramiento_use_case import ProcesarRenombramientoUseCase
from app.use_cases.procesar_separacion_furips_use_case import ProcesarSeparacionFuripsUseCase


class ProcesoRenombramientoWorker(QThread):
    """Ejecuta `ProcesarRenombramientoUseCase` (análisis o renombrado) en un hilo aparte."""

    progreso = Signal(int, int, str)
    finished_ok = Signal(object)  # ResultadoProceso
    finished_error = Signal(str)

    def __init__(
        self,
        carpeta_principal: Path,
        empresa: str,
        tipo_atencion: TipoAtencion,
        fecha_desde: date | None,
        accion: str = "analizar",
        ruta_csv: Path | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._carpeta_principal = carpeta_principal
        self._empresa = empresa
        self._tipo_atencion = tipo_atencion
        self._fecha_desde = fecha_desde
        self._accion = accion
        self._ruta_csv = ruta_csv
        self._use_case = ProcesarRenombramientoUseCase()

    def run(self) -> None:
        try:
            factura_provider = FacturaCsvSource(self._ruta_csv) if self._ruta_csv is not None else None
            metodo = self._use_case.renombrar if self._accion == "renombrar" else self._use_case.analizar
            resultado: ResultadoProceso = metodo(
                self._carpeta_principal,
                self._empresa,
                self._tipo_atencion,
                self._fecha_desde,
                on_progreso=lambda actual, total, msg: self.progreso.emit(actual, total, msg),
                factura_provider=factura_provider,
            )
            self.finished_ok.emit(resultado)
        except ValueError as exc:
            # Ej. el CSV no tiene las columnas requeridas: se informa el motivo puntual.
            self.finished_error.emit(str(exc))
        except Exception:  # noqa: BLE001 - se reporta a la UI, no debe tumbar el hilo
            self.finished_error.emit("No fue posible completar el proceso de renombramiento.")


class ProcesoSeparacionFuripsWorker(QThread):
    """Ejecuta `ProcesarSeparacionFuripsUseCase` (análisis o separación) en un hilo aparte."""

    progreso = Signal(int, int, str)
    finished_ok = Signal(object)  # ResultadoSeparacion
    finished_error = Signal(str)

    def __init__(
        self,
        carpeta_principal: Path,
        accion: str = "analizar",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._carpeta_principal = carpeta_principal
        self._accion = accion
        self._use_case = ProcesarSeparacionFuripsUseCase()

    def run(self) -> None:
        try:
            metodo = self._use_case.separar if self._accion == "separar" else self._use_case.analizar
            resultado: ResultadoSeparacion = metodo(
                self._carpeta_principal,
                on_progreso=lambda actual, total, msg: self.progreso.emit(actual, total, msg),
            )
            self.finished_ok.emit(resultado)
        except Exception:  # noqa: BLE001 - se reporta a la UI, no debe tumbar el hilo
            self.finished_error.emit("No fue posible completar el proceso de separación de FURIPS.")

