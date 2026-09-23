"""Fuente de datos de factura basada en un archivo CSV (alternativa a la consulta a BD).

Reutiliza las mismas reglas de negocio del flujo por base de datos (coincidencia de empresa
vía `EmpresaConfig.coincide_con`) para que la validación/renombrado existentes (que trabajan
sobre `FacturaInfo`) funcionen exactamente igual sin importar el origen del dato.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from app.models.factura_info import FacturaInfo
from app.services.empresas.registro_empresas import obtener_config_empresa

# Columnas que debe tener el CSV (según la estructura acordada con el usuario).
COLUMNAS_REQUERIDAS = (
    "sede",
    "pnto_atncn",
    "pnto_atncn_atncn",
    "dscrp_transcn",
    "cnsctvo_dcto",
    "fcha_dcto",
    "emprs",
    "afldo",
    "cc_afldo",
    "edd",
    "genero",
    "estado",
    "vlr_factrdo",
    "usrio_mdfca",
    "usrio_realiza",
    "lna_prdcto",
    "prfsnl_salud_ordn",
    "prfsnl_salud_rlza",
    "cdgo_prcdmnto",
    "procedimiento",
    "cntdd",
    "vlr_untro",
    "cntdd1",
    "vlr_cnvno",
    "admision",
    "fcha_ingrso_pcnte",
    "nmro_atrzcn_eps",
    "fcha_atrzcn_eps",
)

_FORMATOS_FECHA = ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


def _normalizar_admision(valor: str) -> str:
    """Deja solo los dígitos del valor de la columna `admision` (ej. "CLF   70515" -> "70515")."""
    return "".join(caracter for caracter in (valor or "") if caracter.isdigit())


def _normalizar_fecha(valor: str) -> str:
    """Normaliza la fecha al mismo formato (YYYY-MM-DD) que usa el flujo de base de datos."""
    valor = (valor or "").strip()
    if not valor:
        return ""
    try:
        return date.fromisoformat(valor[:10]).isoformat()
    except ValueError:
        pass
    for formato in _FORMATOS_FECHA:
        try:
            return datetime.strptime(valor, formato).date().isoformat()
        except ValueError:
            continue
    return valor


def _a_numero(valor: str) -> float:
    valor = (valor or "").strip()
    if not valor:
        return 0.0
    try:
        return float(valor)
    except ValueError:
        return 0.0


class FacturaCsvSource:
    """Carga un archivo CSV y permite obtener la `FacturaInfo` asociada a una admisión."""

    def __init__(self, ruta_csv: Path) -> None:
        self._filas_por_admision: dict[str, list[dict[str, str]]] = defaultdict(list)
        self._cargar(ruta_csv)

    def _cargar(self, ruta_csv: Path) -> None:
        with ruta_csv.open(newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)
            columnas = {(nombre or "").strip() for nombre in (lector.fieldnames or [])}
            faltantes = [columna for columna in COLUMNAS_REQUERIDAS if columna not in columnas]
            if faltantes:
                raise ValueError(f"El CSV no contiene las columnas requeridas: {', '.join(faltantes)}")

            for fila in lector:
                admision = _normalizar_admision(fila.get("admision", ""))
                if admision:
                    self._filas_por_admision[admision].append(fila)

    def obtener_factura(self, identificador: str, empresa: str) -> FacturaInfo | None:
        """Busca la factura de la admisión `identificador` (ya normalizada, solo dígitos) y
        suma `cntdd1` de las filas que coincidan en factura (`cnsctvo_dcto`) y empresa."""
        filas = self._filas_por_admision.get(identificador)
        if not filas:
            return None

        cnsctvo_dcto = (filas[0].get("cnsctvo_dcto") or "").strip()
        if not cnsctvo_dcto:
            return None

        config = obtener_config_empresa(empresa)
        coincidentes = [
            fila
            for fila in filas
            if (fila.get("cnsctvo_dcto") or "").strip() == cnsctvo_dcto
            and config.coincide_con(fila.get("emprs", ""))
        ]
        if not coincidentes:
            return None

        referencia = coincidentes[0]
        total = sum(_a_numero(fila.get("cntdd1", "")) for fila in coincidentes)

        numero_factura = cnsctvo_dcto
        if not numero_factura.upper().startswith("SF"):
            numero_factura = f"SF{numero_factura}"

        return FacturaInfo(
            numero_factura=numero_factura,
            empresa=(referencia.get("emprs") or "").strip(),
            fecha_facturacion=_normalizar_fecha(referencia.get("fcha_dcto", "")),
            estado=(referencia.get("estado") or "").strip(),
            usuario_factura=(referencia.get("usrio_realiza") or "").strip(),
            relacion_envio="",
            total=int(round(total)),
        )
