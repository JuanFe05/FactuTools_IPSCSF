"""Registro de configuraciones de validación por empresa (Factory + Strategy paramétrico).

Reglas extraídas de la macro VBA de referencia (soportes obligatorios por empresa y tipo
de atención, grupo alternativo PDX|HEV en Consulta Externa, prefijo de factura y
nomenclatura de carpeta). Agregar una empresa nueva es agregar una entrada aquí, sin
tocar el resto del sistema (Open/Closed Principle).
"""
from __future__ import annotations

from app.models.tipo_atencion import TipoAtencion
from app.services.empresas.empresa_config import EmpresaConfig, ReglaSoportes
from app.services.empresas.validador_por_prefijos import ValidadorPorPrefijos
from app.services.empresas.validador_soportes import ValidadorSoportes

# Consulta Externa: misma lista base para todas las empresas, con grupo alternativo PDX|HEV.
_EXTERNA = ReglaSoportes(prefijos_obligatorios=("FE", "LDP", "OPF"), grupo_alternativo=("PDX", "HEV"))

# Urgencias: lista base y variantes por empresa.
_URGENCIAS_CON_HAU = ReglaSoportes(prefijos_obligatorios=("LDP", "CRC", "HEV", "FE", "HAU"))
_URGECNIAS_SANITAS = ReglaSoportes(prefijos_obligatorios=("LDP", "CRC", "HEV", "FE", "OPF"))
_URGENCIAS_COOSALUD = ReglaSoportes(prefijos_obligatorios=("LDP", "CRC", "HEV", "FE", "HAU", "OPF"))
_URGENCIAS_COMFENALCO = ReglaSoportes(prefijos_obligatorios=("HAU", "LDP", "FE"))
_URGENCIAS_SALUD_TOTAL = ReglaSoportes(
    prefijos_obligatorios=("CRC", "HEV", "LDP", "OPF"), grupo_alternativo=("FE", "FACTURA")
)

_CONFIGS: dict[str, EmpresaConfig] = {
    "COMFENALCO VALLE EPS CONTRIBUTIVO & SUBSIDIADO": EmpresaConfig(
        nombre="COMFENALCO VALLE EPS CONTRIBUTIVO & SUBSIDIADO",
        reglas={TipoAtencion.CONSULTA_EXTERNA: _EXTERNA, TipoAtencion.URGENCIAS: _URGENCIAS_COMFENALCO},
        prefijo_factura="FDE",
    ),
    "COOSALUD CONTRIBUTIVO & SUBSIDIADO": EmpresaConfig(
        nombre="COOSALUD CONTRIBUTIVO & SUBSIDIADO",
        reglas={TipoAtencion.CONSULTA_EXTERNA: _EXTERNA, TipoAtencion.URGENCIAS: _URGENCIAS_COOSALUD},
    ),
    "DISPENSARIO MEDICO DE CALI": EmpresaConfig(
        nombre="DISPENSARIO MEDICO DE CALI",
        reglas={TipoAtencion.CONSULTA_EXTERNA: _EXTERNA, TipoAtencion.URGENCIAS: _URGENCIAS_CON_HAU},
    ),
    "EPS SANITAS CONTRIBUTIVO & SUBSIDIADO": EmpresaConfig(
        nombre="EPS SANITAS CONTRIBUTIVO & SUBSIDIADO",
        reglas={TipoAtencion.CONSULTA_EXTERNA: _EXTERNA, TipoAtencion.URGENCIAS: _URGECNIAS_SANITAS},
        carpeta_incluye_nit=True,
    ),
    "SOS EVENTO FLORIDA CONTRIBUTIVO & SUBSIDIADO": EmpresaConfig(
        nombre="SOS EVENTO FLORIDA CONTRIBUTIVO & SUBSIDIADO",
        reglas={
            TipoAtencion.CONSULTA_EXTERNA: ReglaSoportes(prefijos_obligatorios=("FE", "CRC", "HEV", "LDP")),
            TipoAtencion.URGENCIAS: ReglaSoportes(prefijos_obligatorios=("FE", "CRC", "HEV", "LDP")),
        },
    ),
    # Registradas como dos empresas distintas en la base de datos (contributivo y subsidiado),
    # pero se presentan como una única opción en el select.
    "SALUD TOTAL EPS-S S.A. CONTRIBUTIVO Y SUBSIDIADO": EmpresaConfig(
        nombre="SALUD TOTAL EPS-S S.A.",
        nombres_alternativos=("SALUD TOTAL EPS-S S.A. (SUBSIDIADO)",),
        reglas={TipoAtencion.URGENCIAS: _URGENCIAS_SALUD_TOTAL},
    ),
}


def empresas_disponibles() -> list[str]:
    return list(_CONFIGS.keys())


def obtener_validador(empresa: str) -> ValidadorSoportes:
    config = _CONFIGS.get(empresa) or EmpresaConfig(nombre=empresa)
    return ValidadorPorPrefijos(config)
