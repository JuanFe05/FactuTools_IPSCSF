"""Validador genérico basado en prefijos de PDF, configurado con los datos de una empresa.

Es la única implementación de `ValidadorSoportes`: el comportamiento por empresa se logra
mediante los datos de `EmpresaConfig` (patrón Strategy paramétrico), no mediante una clase
por empresa. Agregar una empresa nueva solo requiere registrar su `EmpresaConfig`.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.models.factura_info import FacturaInfo
from app.models.subcarpeta import ContextoRenombrado, ResultadoValidacion
from app.models.tipo_atencion import TipoAtencion
from app.services.empresas.empresa_config import EmpresaConfig
from app.services.empresas.normalizador import empresas_coinciden

_PATRON_PREFIJO = re.compile(r"[A-Za-z]+")


def _prefijo(nombre_archivo: str) -> str:
    coincidencia = _PATRON_PREFIJO.match(nombre_archivo)
    if not coincidencia:
        return ""
    prefijo = coincidencia.group(0).upper()
    if prefijo in ("FEV", "FDE"):
        return "FE"
    return prefijo


class ValidadorPorPrefijos:
    """Valida soportes obligatorios por prefijo de archivo y aplica la nomenclatura de la empresa."""

    def __init__(self, config: EmpresaConfig) -> None:
        self._config = config

    def extraer_identificador(self, nombre_carpeta: str) -> str | None:
        # Se asume que el nombre de la subcarpeta contiene el número de admisión.
        digitos = "".join(caracter for caracter in nombre_carpeta if caracter.isdigit())
        return digitos or None

    def validar(
        self, pdfs: list[Path], tipo_atencion: TipoAtencion, factura: FacturaInfo | None
    ) -> ResultadoValidacion:
        if factura is None:
            return ResultadoValidacion(
                es_correcto=False, detalles=["No se encontró información de factura en la base de datos."]
            )

        detalles: list[str] = []
        es_correcto = True

        nombres_validos = (self._config.nombre, *self._config.nombres_alternativos)
        if not any(empresas_coinciden(factura.empresa, nombre) for nombre in nombres_validos):
            es_correcto = False
            detalles.append(
                f"La empresa de la factura ({factura.empresa}) no coincide con la empresa seleccionada."
            )

        regla = self._config.reglas.get(tipo_atencion)
        if regla is None:
            detalles.append("No hay reglas de validación configuradas para este tipo de atención.")
            return ResultadoValidacion(es_correcto=False, detalles=detalles)

        prefijos_presentes = {_prefijo(pdf.stem) for pdf in pdfs}

        faltantes = [p for p in regla.prefijos_obligatorios if p not in prefijos_presentes]
        if faltantes:
            es_correcto = False
            detalles.append("Faltan soportes obligatorios: " + ", ".join(faltantes))

        if regla.grupo_alternativo and not any(p in prefijos_presentes for p in regla.grupo_alternativo):
            es_correcto = False
            detalles.append("Falta al menos uno de: " + " o ".join(regla.grupo_alternativo))

        if es_correcto:
            encontrados = list(regla.prefijos_obligatorios)
            if regla.grupo_alternativo:
                encontrados += [p for p in regla.grupo_alternativo if p in prefijos_presentes]
            detalles.append("Soportes obligatorios encontrados: " + ", ".join(encontrados))

        return ResultadoValidacion(es_correcto=es_correcto, detalles=detalles)

    def nombre_nuevo_archivo(self, pdf: Path, contexto: ContextoRenombrado) -> str:
        if contexto.factura is None or not contexto.factura.numero_factura:
            return pdf.name

        num_factura = contexto.factura.numero_factura.strip()
        if not num_factura.upper().startswith("SF"):
            num_factura = f"SF{num_factura}"

        coincidencia = _PATRON_PREFIJO.match(pdf.stem)
        prefijo_detectado = coincidencia.group(0).upper() if coincidencia else ""
        if not prefijo_detectado:
            return pdf.name

        if prefijo_detectado in ("FE", "FEV", "FDE", "FACTURA"):
            tipo_documento = self._config.prefijo_factura
        else:
            tipo_documento = prefijo_detectado

        return f"{tipo_documento}_{self._config.nit_ips}_{num_factura}{pdf.suffix}"

    def nombre_nueva_carpeta(self, contexto: ContextoRenombrado) -> str:
        if contexto.factura is None or not contexto.factura.numero_factura:
            return contexto.subcarpeta.nombre

        num_factura = contexto.factura.numero_factura.strip()
        if not num_factura.upper().startswith("SF"):
            num_factura = f"SF{num_factura}"

        if self._config.carpeta_incluye_nit:
            # Usar NIT fijo de la empresa (configurado en EmpresaConfig), no el NIT de la factura
            return f"{self._config.nit_ips}_{num_factura}"
        return num_factura
