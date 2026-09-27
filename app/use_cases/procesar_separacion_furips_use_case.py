"""Caso de uso: separar archivos FURIPS por número de factura en subcarpetas."""
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

from app.models.furips import FuripsFile, ResultadoFactura, ResultadoSeparacion, SplitTask
from app.services.furips.parser import FuripsParserFactory
from app.services.furips.scanner import FuripsFileScanner
from app.services.furips.writer import FuripsWriter

logger = logging.getLogger(__name__)

ProgresoCallback = Callable[[int, int, str], None]


class ProcesarSeparacionFuripsUseCase:
    """Orquesta el flujo: escanear archivos FURIPS1/FURIPS2, agrupar por factura y
    (opcionalmente) escribir los archivos separados en subcarpetas.

    `analizar()` deja la información cargada en la tabla sin tocar el sistema de archivos.
    `separar()` repite el mismo análisis y, además, crea las carpetas y escribe los archivos.
    """

    def __init__(
        self,
        scanner: FuripsFileScanner | None = None,
        parser_factory: type[FuripsParserFactory] = FuripsParserFactory,
        writer: FuripsWriter | None = None,
    ) -> None:
        self._scanner = scanner or FuripsFileScanner()
        self._parser_factory = parser_factory
        self._writer = writer or FuripsWriter()

    def analizar(
        self, carpeta_principal: Path, on_progreso: ProgresoCallback | None = None
    ) -> ResultadoSeparacion:
        return self._procesar(carpeta_principal, separar=False, on_progreso=on_progreso)

    def separar(
        self, carpeta_principal: Path, on_progreso: ProgresoCallback | None = None
    ) -> ResultadoSeparacion:
        return self._procesar(carpeta_principal, separar=True, on_progreso=on_progreso)

    def _procesar(
        self, carpeta_principal: Path, separar: bool, on_progreso: ProgresoCallback | None
    ) -> ResultadoSeparacion:
        furips_files = self._scanner.scan(carpeta_principal)
        por_factura = self._agrupar_por_factura(furips_files)

        resultado = ResultadoSeparacion(
            total_txt_encontrados=len(furips_files),
            carpetas_a_crear=len(por_factura),
        )

        total = len(por_factura)
        for indice, folder_id in enumerate(sorted(por_factura), start=1):
            if on_progreso:
                verbo = "Separando" if separar else "Analizando"
                on_progreso(indice, total, f"{verbo} factura {indice} de {total}")

            tareas = por_factura[folder_id]
            resultado_factura = ResultadoFactura(
                numero_factura=folder_id,
                furips1_generado=any(t.output_prefix == "FURIPS1" for t in tareas),
                furips2_generado=any(t.output_prefix == "FURIPS2" for t in tareas),
            )

            if separar:
                try:
                    for tarea in tareas:
                        self._writer.write(carpeta_principal, tarea)
                    resultado_factura.carpeta_creada = True
                    resultado_factura.separado_correctamente = True
                except OSError:
                    logger.exception("Error separando la factura %s", folder_id)
                    resultado_factura.error = "No fue posible crear la carpeta o escribir los archivos."

            resultado.facturas.append(resultado_factura)

        if separar:
            resultado.carpetas_creadas = sum(1 for f in resultado.facturas if f.carpeta_creada)

        return resultado

    def _agrupar_por_factura(self, furips_files: list[FuripsFile]) -> dict[str, list[SplitTask]]:
        por_factura: dict[str, list[SplitTask]] = defaultdict(list)

        for furips_file in furips_files:
            parser = self._parser_factory.create(furips_file.prefix)
            records = parser.parse(furips_file.path)

            lineas_por_factura: dict[str, list[str]] = defaultdict(list)
            for record in records:
                lineas_por_factura[record.folder_id].append(record.raw_line)

            for folder_id, lineas in lineas_por_factura.items():
                por_factura[folder_id].append(
                    SplitTask(folder_id=folder_id, output_prefix=parser.output_prefix, lines=lineas)
                )

        return por_factura
