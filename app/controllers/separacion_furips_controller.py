"""Controlador para el flujo de separación de archivos FURIPS."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.controllers.workers import ProcesoSeparacionFuripsWorker
from app.models.furips import ResultadoSeparacion
from app.services.furips.scanner import FuripsFileScanner

logger = logging.getLogger(__name__)


class SeparacionFuripsController(QObject):
    """Coordina la selección de carpeta y el proceso de análisis y separación de
    archivos FURIPS1/FURIPS2 en subcarpetas por número de factura."""

    carpetaSeleccionadaChanged = Signal()
    analisisActualizado = Signal()
    resultadosChanged = Signal()
    procesandoChanged = Signal()
    progresoChanged = Signal()
    separarHabilitadoChanged = Signal()
    accionActualChanged = Signal()
    procesoTerminado = Signal(dict)
    procesoError = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._carpeta_seleccionada = ""
        self._total_txt_encontrados = 0
        self._errores_previos: list[str] = []
        self._resultados: list[dict] = []
        self._carpetas_a_crear = 0
        self._carpetas_creadas = 0
        self._procesando = False
        self._progreso_actual = 0
        self._progreso_total = 0
        self._mensaje_progreso = ""
        self._accion_actual = ""
        self._scanner = FuripsFileScanner()
        self._worker: ProcesoSeparacionFuripsWorker | None = None

    @Property(str, notify=carpetaSeleccionadaChanged)
    def carpetaSeleccionada(self) -> str:
        return self._carpeta_seleccionada

    @Property(int, notify=analisisActualizado)
    def totalTxtEncontrados(self) -> int:
        return self._total_txt_encontrados

    @Property("QVariant", notify=analisisActualizado)
    def erroresPrevios(self) -> list[str]:
        return self._errores_previos

    @Property("QVariant", notify=resultadosChanged)
    def resultados(self) -> list[dict]:
        return self._resultados

    @Property(int, notify=resultadosChanged)
    def carpetasACrear(self) -> int:
        return self._carpetas_a_crear

    @Property(int, notify=resultadosChanged)
    def carpetasCreadas(self) -> int:
        return self._carpetas_creadas

    @Property(int, notify=resultadosChanged)
    def facturasConError(self) -> int:
        return sum(1 for r in self._resultados if r.get("error"))

    @Property(bool, notify=procesandoChanged)
    def procesando(self) -> bool:
        return self._procesando

    @Property(int, notify=progresoChanged)
    def progresoActual(self) -> int:
        return self._progreso_actual

    @Property(int, notify=progresoChanged)
    def progresoTotal(self) -> int:
        return self._progreso_total

    @Property(str, notify=progresoChanged)
    def mensajeProgreso(self) -> str:
        return self._mensaje_progreso

    @Property(str, notify=accionActualChanged)
    def accionActual(self) -> str:
        return self._accion_actual

    @Property(bool, notify=separarHabilitadoChanged)
    def hayDatosCargados(self) -> bool:
        """Determina si "Borrar todo" debe estar habilitado."""
        return bool(self._carpeta_seleccionada or self._resultados)

    @Property(bool, notify=separarHabilitadoChanged)
    def separarHabilitado(self) -> bool:
        """El botón "Separar" solo se habilita cuando ya hay un análisis con archivos
        FURIPS detectados y sin errores previos de lectura de carpeta."""
        return (
            bool(self._carpeta_seleccionada)
            and self._total_txt_encontrados > 0
            and len(self._errores_previos) == 0
            and not self._procesando
        )

    @Slot(QUrl)
    def seleccionarCarpeta(self, url: QUrl) -> None:
        """Guarda la carpeta elegida y hace un análisis previo (conteo de archivos FURIPS)."""
        ruta = url.toLocalFile()
        if not ruta:
            return
        self._carpeta_seleccionada = ruta
        self.carpetaSeleccionadaChanged.emit()
        logger.info("Carpeta de archivos FURIPS seleccionada: %s", ruta)

        # Una carpeta nueva invalida cualquier resultado de un análisis anterior.
        self._resultados = []
        self._carpetas_a_crear = 0
        self._carpetas_creadas = 0
        self.resultadosChanged.emit()

        errores: list[str] = []
        try:
            furips_files = self._scanner.scan(Path(ruta))
        except OSError:
            logger.exception("Error analizando la carpeta %s", ruta)
            furips_files = []
            errores.append("No fue posible leer la carpeta seleccionada.")

        if not furips_files and not errores:
            errores.append("No se encontraron archivos FURIPS1 o FURIPS2 en la carpeta seleccionada.")

        self._total_txt_encontrados = len(furips_files)
        self._errores_previos = errores
        self.analisisActualizado.emit()
        self.separarHabilitadoChanged.emit()

    @Slot()
    def analizar(self) -> None:
        """Lanza el worker de análisis (detectar archivos + agrupar por factura) en
        segundo plano, usando la carpeta ya almacenada."""
        self._lanzar_worker(accion="analizar")

    @Slot()
    def ejecutarSeparacion(self) -> None:
        """Lanza el worker de separación real (crea carpetas y escribe los archivos)."""
        self._lanzar_worker(accion="separar")

    def _lanzar_worker(self, accion: str) -> None:
        if not self._carpeta_seleccionada or self._procesando:
            return

        self._procesando = True
        self._accion_actual = accion
        self._progreso_actual = 0
        self._progreso_total = 0
        self._mensaje_progreso = "Iniciando..."
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.progresoChanged.emit()
        self.separarHabilitadoChanged.emit()

        self._worker = ProcesoSeparacionFuripsWorker(
            Path(self._carpeta_seleccionada),
            accion=accion,
        )
        self._worker.progreso.connect(self._en_progreso)
        self._worker.finished_ok.connect(self._en_finalizado)
        self._worker.finished_error.connect(self._en_error)
        self._worker.start()

    @Slot()
    def borrarTodo(self) -> None:
        """Limpia por completo el proceso actual (carpeta, resultados e indicadores)
        para iniciar uno nuevo."""
        self._carpeta_seleccionada = ""
        self._total_txt_encontrados = 0
        self._errores_previos = []
        self._resultados = []
        self._carpetas_a_crear = 0
        self._carpetas_creadas = 0
        self.carpetaSeleccionadaChanged.emit()
        self.analisisActualizado.emit()
        self.resultadosChanged.emit()
        self.separarHabilitadoChanged.emit()

    def _en_progreso(self, actual: int, total: int, mensaje: str) -> None:
        self._progreso_actual = actual
        self._progreso_total = total
        self._mensaje_progreso = mensaje
        self.progresoChanged.emit()

    def _en_finalizado(self, resultado: ResultadoSeparacion) -> None:
        accion_finalizada = self._accion_actual
        self._procesando = False
        self._accion_actual = ""
        self._resultados = [f.a_diccionario() for f in resultado.facturas]
        self._carpetas_a_crear = resultado.carpetas_a_crear
        self._carpetas_creadas = resultado.carpetas_creadas
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.resultadosChanged.emit()
        self.separarHabilitadoChanged.emit()
        resumen = resultado.a_resumen()
        resumen["accion"] = accion_finalizada
        self.procesoTerminado.emit(resumen)

    def _en_error(self, mensaje: str) -> None:
        self._procesando = False
        self._accion_actual = ""
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.separarHabilitadoChanged.emit()
        self.procesoError.emit(mensaje)
