"""Controlador para el flujo de renombramiento de soportes."""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from app.controllers.workers import ProcesoRenombramientoWorker
from app.models.subcarpeta import ResultadoProceso
from app.models.tipo_atencion import TipoAtencion
from app.services.empresas.registro_empresas import empresas_disponibles
from app.services.processors.carpeta_scanner import escanear_carpeta_principal

logger = logging.getLogger(__name__)


class RenombrarController(QObject):
    """Coordina la selección de carpeta/empresa/tipo de atención/fecha y el proceso de
    análisis y renombramiento de soportes."""

    carpetaSeleccionadaChanged = Signal()
    analisisActualizado = Signal()
    resultadosChanged = Signal()
    procesandoChanged = Signal()
    progresoChanged = Signal()
    renombrarHabilitadoChanged = Signal()
    accionActualChanged = Signal()
    procesoTerminado = Signal(dict)
    procesoError = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._carpeta_seleccionada = ""
        self._empresa_seleccionada = ""
        self._tipo_atencion = ""
        self._fecha_desde = ""
        self._total_subcarpetas = 0
        self._total_pdfs = 0
        self._errores_previos: list[str] = []
        self._resultados: list[dict] = []
        self._procesando = False
        self._progreso_actual = 0
        self._progreso_total = 0
        self._mensaje_progreso = ""
        self._accion_actual = ""
        self._worker: ProcesoRenombramientoWorker | None = None

    @Property(str, notify=carpetaSeleccionadaChanged)
    def carpetaSeleccionada(self) -> str:
        return self._carpeta_seleccionada

    @Property(str, notify=renombrarHabilitadoChanged)
    def empresaSeleccionada(self) -> str:
        return self._empresa_seleccionada

    @Property(str, notify=renombrarHabilitadoChanged)
    def tipoAtencion(self) -> str:
        return self._tipo_atencion

    @Property(str, notify=renombrarHabilitadoChanged)
    def fechaDesde(self) -> str:
        return self._fecha_desde

    @Property(int, notify=analisisActualizado)
    def totalSubcarpetas(self) -> int:
        return self._total_subcarpetas

    @Property(int, notify=analisisActualizado)
    def totalPdfs(self) -> int:
        return self._total_pdfs

    @Property("QVariant", notify=analisisActualizado)
    def erroresPrevios(self) -> list[str]:
        return self._errores_previos

    @Property("QVariant", constant=True)
    def empresasDisponibles(self) -> list[str]:
        return empresas_disponibles()

    @Property("QVariant", notify=resultadosChanged)
    def resultados(self) -> list[dict]:
        return self._resultados

    @Property(int, notify=resultadosChanged)
    def totalRegistrosEncontrados(self) -> int:
        return sum(1 for r in self._resultados if r.get("registroEncontrado"))

    @Property(int, notify=resultadosChanged)
    def totalRegistrosNoEncontrados(self) -> int:
        return sum(1 for r in self._resultados if not r.get("registroEncontrado"))

    @Property(int, notify=resultadosChanged)
    def totalGeneral(self) -> int:
        return sum(r.get("total", 0) for r in self._resultados)

    @Property(int, notify=resultadosChanged)
    def carpetasConErrores(self) -> int:
        return sum(1 for r in self._resultados if r.get("archivosCorrectos") is False)

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

    @Property(bool, notify=renombrarHabilitadoChanged)
    def hayDatosCargados(self) -> bool:
        """Determina si "Borrar todo" debe estar habilitado."""
        return bool(
            self._carpeta_seleccionada
            or self._empresa_seleccionada
            or self._tipo_atencion
            or self._fecha_desde
            or self._resultados
        )

    @Property(bool, notify=renombrarHabilitadoChanged)
    def renombrarHabilitado(self) -> bool:
        """El botón "Renombrar" del dashboard solo se habilita cuando ya hay un análisis
        completo (empresa + tipo de atención + fecha + carpeta + resultados) y sin
        errores críticos."""
        return (
            bool(self._empresa_seleccionada)
            and bool(self._tipo_atencion)
            and bool(self._fecha_desde)
            and bool(self._carpeta_seleccionada)
            and self._total_subcarpetas > 0
            and len(self._errores_previos) == 0
            and len(self._resultados) > 0
            and not self._procesando
        )

    @Slot(str)
    def seleccionarEmpresa(self, empresa: str) -> None:
        """Persiste la empresa elegida en el estado del proceso."""
        if empresa != self._empresa_seleccionada:
            self._empresa_seleccionada = empresa
            self.renombrarHabilitadoChanged.emit()

    @Slot(str)
    def seleccionarTipoAtencion(self, tipo_atencion: str) -> None:
        if tipo_atencion != self._tipo_atencion:
            self._tipo_atencion = tipo_atencion
            self.renombrarHabilitadoChanged.emit()

    @Slot(str)
    def establecerFechaDesde(self, fecha_iso: str) -> None:
        if fecha_iso != self._fecha_desde:
            self._fecha_desde = fecha_iso
            self.renombrarHabilitadoChanged.emit()

    @Slot(QUrl)
    def seleccionarCarpeta(self, url: QUrl) -> None:
        """Guarda la carpeta elegida y hace un análisis previo (conteo de subcarpetas/PDFs)."""
        ruta = url.toLocalFile()
        if not ruta:
            return
        self._carpeta_seleccionada = ruta
        self.carpetaSeleccionadaChanged.emit()
        logger.info("Carpeta de soportes seleccionada: %s", ruta)

        # Una carpeta nueva invalida cualquier resultado de un análisis anterior.
        self._resultados = []
        self.resultadosChanged.emit()

        errores: list[str] = []
        try:
            subcarpetas = escanear_carpeta_principal(Path(ruta))
        except OSError:
            logger.exception("Error analizando la carpeta %s", ruta)
            subcarpetas = []
            errores.append("No fue posible leer la carpeta seleccionada.")

        if not subcarpetas and not errores:
            errores.append("No se encontraron subcarpetas en la carpeta seleccionada.")

        self._total_subcarpetas = len(subcarpetas)
        self._total_pdfs = sum(len(s.pdfs) for s in subcarpetas)
        self._errores_previos = errores
        self.analisisActualizado.emit()
        self.renombrarHabilitadoChanged.emit()

    @Slot()
    def analizar(self) -> None:
        """Lanza el worker de análisis (detectar subcarpetas + consultar BD) en segundo
        plano, usando el estado ya almacenado (empresa/tipo de atención/fecha/carpeta)."""
        self._lanzar_worker(accion="analizar")

    @Slot()
    def ejecutarRenombrado(self) -> None:
        """Lanza el worker de renombrado real (solo para subcarpetas ya validadas como
        correctas), usando el mismo estado almacenado."""
        self._lanzar_worker(accion="renombrar")

    def _lanzar_worker(self, accion: str) -> None:
        fecha = self._fecha_desde_como_date()
        if (
            not self._empresa_seleccionada
            or not self._tipo_atencion
            or fecha is None
            or not self._carpeta_seleccionada
            or self._procesando
        ):
            return

        self._procesando = True
        self._accion_actual = accion
        self._progreso_actual = 0
        self._progreso_total = self._total_subcarpetas
        self._mensaje_progreso = "Iniciando..."
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.progresoChanged.emit()
        self.renombrarHabilitadoChanged.emit()

        self._worker = ProcesoRenombramientoWorker(
            Path(self._carpeta_seleccionada),
            self._empresa_seleccionada,
            TipoAtencion(self._tipo_atencion),
            fecha,
            accion=accion,
        )
        self._worker.progreso.connect(self._en_progreso)
        self._worker.finished_ok.connect(self._en_finalizado)
        self._worker.finished_error.connect(self._en_error)
        self._worker.start()

    def _fecha_desde_como_date(self) -> date | None:
        try:
            return date.fromisoformat(self._fecha_desde)
        except (TypeError, ValueError):
            return None

    @Slot()
    def borrarTodo(self) -> None:
        """Limpia por completo el proceso actual (empresa, tipo de atención, fecha,
        carpeta, resultados e indicadores) para iniciar uno nuevo."""
        self._carpeta_seleccionada = ""
        self._empresa_seleccionada = ""
        self._tipo_atencion = ""
        self._fecha_desde = ""
        self._total_subcarpetas = 0
        self._total_pdfs = 0
        self._errores_previos = []
        self._resultados = []
        self.carpetaSeleccionadaChanged.emit()
        self.analisisActualizado.emit()
        self.resultadosChanged.emit()
        self.renombrarHabilitadoChanged.emit()

    def _en_progreso(self, actual: int, total: int, mensaje: str) -> None:
        self._progreso_actual = actual
        self._progreso_total = total
        self._mensaje_progreso = mensaje
        self.progresoChanged.emit()

    def _en_finalizado(self, resultado: ResultadoProceso) -> None:
        accion_finalizada = self._accion_actual
        self._procesando = False
        self._accion_actual = ""
        self._resultados = [s.a_diccionario() for s in resultado.subcarpetas]
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.resultadosChanged.emit()
        self.renombrarHabilitadoChanged.emit()
        resumen = resultado.a_resumen()
        resumen["accion"] = accion_finalizada
        self.procesoTerminado.emit(resumen)

    def _en_error(self, mensaje: str) -> None:
        self._procesando = False
        self._accion_actual = ""
        self.procesandoChanged.emit()
        self.accionActualChanged.emit()
        self.renombrarHabilitadoChanged.emit()
        self.procesoError.emit(mensaje)
