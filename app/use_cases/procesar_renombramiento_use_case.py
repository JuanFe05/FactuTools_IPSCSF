"""Caso de uso: analizar, validar y renombrar soportes (subcarpetas + PDFs) de una empresa."""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date
from pathlib import Path

from app.models.estado_renombramiento import EstadoRenombramiento
from app.models.factura_info import FacturaInfo
from app.models.subcarpeta import (
    ContextoRenombrado,
    ResultadoProceso,
    ResultadoSubcarpeta,
    SubcarpetaDetectada,
)
from app.models.tipo_atencion import TipoAtencion
from app.repositories.factura_repository import FacturaRepository
from app.services.empresas.registro_empresas import obtener_validador
from app.services.empresas.validador_soportes import ValidadorSoportes
from app.services.processors.carpeta_scanner import escanear_carpeta_principal

logger = logging.getLogger(__name__)

ProgresoCallback = Callable[[int, int, str], None]


class ProcesarRenombramientoUseCase:
    """Orquesta el flujo: escanear, consultar BD, validar y (opcionalmente) renombrar.

    `analizar()` deja la información cargada en la tabla sin tocar el sistema de archivos.
    `renombrar()` repite el mismo análisis y, además, renombra los archivos/carpetas que
    hayan validado correctamente.
    """

    def __init__(self, factura_repository: FacturaRepository | None = None) -> None:
        self._factura_repository = factura_repository or FacturaRepository()

    def analizar(
        self,
        carpeta_principal: Path,
        empresa: str,
        tipo_atencion: TipoAtencion,
        fecha_desde: date,
        on_progreso: ProgresoCallback | None = None,
    ) -> ResultadoProceso:
        return self._procesar(
            carpeta_principal, empresa, tipo_atencion, fecha_desde, renombrar=False, on_progreso=on_progreso
        )

    def renombrar(
        self,
        carpeta_principal: Path,
        empresa: str,
        tipo_atencion: TipoAtencion,
        fecha_desde: date,
        on_progreso: ProgresoCallback | None = None,
    ) -> ResultadoProceso:
        return self._procesar(
            carpeta_principal, empresa, tipo_atencion, fecha_desde, renombrar=True, on_progreso=on_progreso
        )

    def _procesar(
        self,
        carpeta_principal: Path,
        empresa: str,
        tipo_atencion: TipoAtencion,
        fecha_desde: date,
        renombrar: bool,
        on_progreso: ProgresoCallback | None,
    ) -> ResultadoProceso:
        validador = obtener_validador(empresa)
        subcarpetas = escanear_carpeta_principal(carpeta_principal)
        total = len(subcarpetas)
        resultado = ResultadoProceso(total_pdfs=sum(len(s.pdfs) for s in subcarpetas))

        for indice, subcarpeta in enumerate(subcarpetas, start=1):
            if on_progreso:
                verbo = "Renombrando" if renombrar else "Consultando"
                on_progreso(indice, total, f"{verbo} carpeta {indice} de {total}")

            identificador = validador.extraer_identificador(subcarpeta.nombre)
            factura = (
                self._factura_repository.obtener_por_identificador(
                    identificador, fecha_desde, tipo_atencion=tipo_atencion
                )
                if identificador
                else None
            )
            validacion = validador.validar(subcarpeta.pdfs, tipo_atencion, factura)

            estado_renombramiento = EstadoRenombramiento.PENDIENTE
            motivo_error = ""
            archivos_renombrados = 0
            carpeta_renombrada = False

            if renombrar:
                # La coincidencia de empresa ya la evalúa `validador.validar()` (con
                # normalización de sufijos de régimen), por lo que no se repite aquí con
                # una comparación estricta de strings (eso nunca coincidía y bloqueaba
                # el renombrado de empresas como COOSALUD, EPS SANITAS, etc.).
                if factura is not None and validacion.es_correcto:
                    estado_renombramiento, motivo_error, archivos_renombrados, carpeta_renombrada = (
                        self._renombrar_subcarpeta(subcarpeta, validador, empresa, factura)
                    )
                else:
                    estado_renombramiento = EstadoRenombramiento.ERROR
                    if factura is None:
                        motivo_error = "No se renombró: no se encontró información de factura."
                    else:
                        motivo_error = "No se renombró: la validación de soportes no fue correcta (Correcto = No)."

            resultado.archivos_renombrados += archivos_renombrados
            resultado.carpetas_renombradas += 1 if carpeta_renombrada else 0

            resultado.subcarpetas.append(
                ResultadoSubcarpeta(
                    nombre_carpeta=subcarpeta.nombre,
                    numero_factura=factura.numero_factura if factura else "",
                    registro_encontrado=factura is not None,
                    archivos_correctos=validacion.es_correcto,
                    empresa=factura.empresa if factura else "",
                    fecha_facturacion=factura.fecha_facturacion if factura else "",
                    estado=factura.estado if factura else "",
                    usuario_factura=factura.usuario_factura if factura else "",
                    relacion_envio=factura.relacion_envio if factura else "",
                    total=factura.total if factura else 0,
                    estado_renombramiento=estado_renombramiento,
                    detalles_validacion=validacion.detalles,
                    motivo_error=motivo_error,
                )
            )

        return resultado

    def _renombrar_subcarpeta(
        self,
        subcarpeta: SubcarpetaDetectada,
        validador: ValidadorSoportes,
        empresa: str,
        factura: FacturaInfo,
    ) -> tuple[EstadoRenombramiento, str, int, bool]:
        contexto = ContextoRenombrado(subcarpeta=subcarpeta, factura=factura, empresa=empresa)
        archivos_renombrados = 0
        carpeta_renombrada = False
        try:
            nombres_asignados: set[str] = set()
            for pdf in subcarpeta.pdfs:
                nuevo_nombre = validador.nombre_nuevo_archivo(pdf, contexto)
                if not nuevo_nombre:
                    continue

                nombre_final = nuevo_nombre
                if nombre_final in nombres_asignados:
                    stem = Path(nuevo_nombre).stem
                    suffix = Path(nuevo_nombre).suffix
                    contador = 2
                    while f"{stem}_{contador}{suffix}" in nombres_asignados:
                        contador += 1
                    nombre_final = f"{stem}_{contador}{suffix}"

                nombres_asignados.add(nombre_final)

                if nombre_final != pdf.name:
                    pdf.rename(pdf.with_name(nombre_final))
                    archivos_renombrados += 1

            nueva_carpeta = validador.nombre_nueva_carpeta(contexto)
            if nueva_carpeta and nueva_carpeta != subcarpeta.nombre:
                destino_carpeta = subcarpeta.ruta.with_name(nueva_carpeta)
                if not destino_carpeta.exists():
                    subcarpeta.ruta.rename(destino_carpeta)
                    carpeta_renombrada = True
                else:
                    logger.warning("La carpeta destino %s ya existe.", destino_carpeta)

            return EstadoRenombramiento.COMPLETADO, "", archivos_renombrados, carpeta_renombrada
        except OSError:
            logger.exception("Error renombrando la subcarpeta %s", subcarpeta.ruta)
            return (
                EstadoRenombramiento.ERROR,
                "No fue posible renombrar uno o más archivos/carpetas.",
                archivos_renombrados,
                carpeta_renombrada,
            )
