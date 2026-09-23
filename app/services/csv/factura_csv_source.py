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
    """Parsea números en formatos europeos (15.360,00) y estadounidenses (15,360.00)."""
    valor = (valor or "").strip()
    if not valor:
        return 0.0
    
    puntos = valor.count(".")
    comas = valor.count(",")
    
    # Regla: el separador más a la DERECHA es el decimal; los demás son de miles
    if puntos == 0 and comas == 0:
        # Sin separadores: "15360"
        pass
    elif puntos == 0 and comas == 1:
        # Solo comas: "15,360" → coma es decimal
        valor = valor.replace(",", ".")
    elif puntos == 1 and comas == 0:
        # Solo punto: "15.360" → punto es decimal
        pass
    elif puntos > 0 and comas > 0:
        # Ambos: detectar cuál es decimal (más a la derecha)
        if valor.rfind(",") > valor.rfind("."):
            # "15.360,00" → coma es decimal (formato europeo)
            valor = valor.replace(".", "").replace(",", ".")
        else:
            # "15,360.00" → punto es decimal (formato US)
            valor = valor.replace(",", "")
    elif puntos > 1:
        # "15.360.000" → dividir por último punto
        partes = valor.rsplit(".", 1)
        valor = (partes[0].replace(".", "") + "." + partes[1]) if len(partes) > 1 else partes[0]
    elif comas > 1:
        # "15,360,000" → dividir por última coma
        partes = valor.rsplit(",", 1)
        valor = (partes[0].replace(",", "") + "." + partes[1]) if len(partes) > 1 else partes[0]
    
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
            # Detectar delimitador automáticamente (,; o tabulador)
            muestra = archivo.read(8192)  # Leer primeras líneas para detectar
            archivo.seek(0)  # Volver al inicio
            try:
                delimitador = csv.Sniffer().sniff(muestra, delimiters=",;\t").delimiter
            except csv.Error:
                delimitador = ","  # Fallback por defecto
            
            lector = csv.DictReader(archivo, delimiter=delimitador)
            columnas = {(nombre or "").strip() for nombre in (lector.fieldnames or [])}
            faltantes = [columna for columna in COLUMNAS_REQUERIDAS if columna not in columnas]
            if faltantes:
                raise ValueError(f"El CSV no contiene las columnas requeridas: {', '.join(faltantes)}")

            for fila in lector:
                admision = _normalizar_admision(fila.get("admision", ""))
                if admision:
                    self._filas_por_admision[admision].append(fila)

    def obtener_factura(self, identificador: str, empresa: str) -> FacturaInfo | None:
        """Busca la admisión `identificador` y suma cntdd1 de TODOS los registros de esa
        admisión, sin filtrar por empresa, número de factura ni otros campos. Retorna la
        información de referencia (primer registro) pero con el total acumulado."""
        filas = self._filas_por_admision.get(identificador)
        if not filas:
            return None

        referencia = filas[0]
        
        # Sumar TODOS los cntdd1 de la admisión (regla: GROUP BY admision, sin otros filtros)
        total = sum(_a_numero(fila.get("cntdd1", "")) for fila in filas)

        cnsctvo_dcto = (referencia.get("cnsctvo_dcto") or "").strip()
        if not cnsctvo_dcto:
            cnsctvo_dcto = "SIN_FACTURA"

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
