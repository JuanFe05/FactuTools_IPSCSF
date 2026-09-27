"""Obtiene la información de factura asociada a una subcarpeta, desde SQL Server."""
from __future__ import annotations

import logging
from datetime import date

from app.core.exceptions import DatabaseError
from app.models.factura_info import FacturaInfo
from app.models.tipo_atencion import TipoAtencion
from app.services.database.connection import SqlServerConnection

logger = logging.getLogger(__name__)

# Consulta propia, reducida y parametrizada por número de admisión (NO es la query de
# reporte completa; solo conserva los JOIN indispensables para resolver No. Factura,
# Empresa, F. Facturación, Estado, Usuario, NIT y Total, y el vínculo admisión<->transacción).
# El filtro de fechas se aplica como rango (fecha_desde <= fcha_dcto <= fecha_hasta) en la propia
# consulta (no se trae el histórico completo para filtrar en el frontend).
# El Total se calcula sumando todos los cntdd1 (cntdd * vlr_untro) asociados al documento.
# Validada contra la base de datos real: admisiones sin factura asociada retornan None
# correctamente, admisiones facturadas devuelven los datos esperados.
_CONSULTA_FACTURA_POR_ADMISION = """
WITH cte_adm AS (
    SELECT unco_trnsccn, MAX(cnsctvo_admsns) AS cnsctvo_admsns
    FROM (
        SELECT asd.unco_trnsccn, adm.cnsctvo_admsns
        FROM tbAdmisionesServiciosDetalle        asd    WITH (NOLOCK)
        JOIN tbAdmisionesEmpresasPuntosAtencion  aep    WITH (NOLOCK) ON aep.unco    = asd.unco_admsn_emprss_pnts_atncn
        JOIN tbAdmisionesEmpresas                ae_adm WITH (NOLOCK) ON ae_adm.unco = aep.unco_admsns_emprss
        JOIN tbAdmisiones                        adm    WITH (NOLOCK) ON adm.unco    = ae_adm.unco_admsns
        UNION
        SELECT smd.unco_trnsccn, adm.cnsctvo_admsns
        FROM tbAdmisionesSuministrosDetalle      smd    WITH (NOLOCK)
        JOIN tbAdmisionesEmpresasPuntosAtencion  aep    WITH (NOLOCK) ON aep.unco    = smd.unco_admsn_emprss_pnts_atncn
        JOIN tbAdmisionesEmpresas                ae_adm WITH (NOLOCK) ON ae_adm.unco = aep.unco_admsns_emprss
        JOIN tbAdmisiones                        adm    WITH (NOLOCK) ON adm.unco    = ae_adm.unco_admsns
    ) x
    GROUP BY unco_trnsccn
),
cte_totales_trnsccn AS (
    SELECT unco_trnsccn, ISNULL(SUM(total_detalle), 0) AS total_trnsccn
    FROM (
        SELECT ts.unco_trnsccn, CAST(ts.cntdd * ts.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesServicios ts WITH (NOLOCK)
        UNION ALL
        SELECT tsu.unco_trnsccn, CAST(tsu.cntdd * tsu.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesSuministros tsu WITH (NOLOCK)
    ) detalles
    GROUP BY unco_trnsccn
),
cte_totales_fctra AS (
    SELECT fa.unco, ISNULL(SUM(total_detalle), 0) AS total_fctra
    FROM tbFacturasAgrupadas fa WITH (NOLOCK)
    JOIN tbTransaccionesFacturasAgrupadas tfa WITH (NOLOCK) ON tfa.unco_fctra_agrpda = fa.unco
    JOIN tbTransacciones t WITH (NOLOCK) ON t.unco = tfa.unco_trnsccn
    LEFT JOIN (
        SELECT ts.unco_trnsccn, CAST(ts.cntdd * ts.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesServicios ts WITH (NOLOCK)
        UNION ALL
        SELECT tsu.unco_trnsccn, CAST(tsu.cntdd * tsu.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesSuministros tsu WITH (NOLOCK)
    ) detalles ON detalles.unco_trnsccn = t.unco
    GROUP BY fa.unco
)
SELECT TOP (1) cnsctvo_dcto, emprs, fcha_dcto, estado, usrio_realiza, nit, total_valor
FROM (
    SELECT TOP (1)
        t.cnsctvo_dcto                                    AS cnsctvo_dcto,
        LTRIM(RTRIM(ISNULL(t.dscrpcn_emprsa_crta, '')))    AS emprs,
        CONVERT(VARCHAR(10), t.fcha_dcto, 23)              AS fcha_dcto,
        ISNULL(LTRIM(RTRIM(er.dscrpcn)), '')               AS estado,
        LTRIM(RTRIM(ISNULL(lgn.dscrpcn, '')))              AS usrio_realiza,
        ISNULL(t.nmro_idntfccn, '')                        AS nit,
        ISNULL(tt.total_trnsccn, 0)                        AS total_valor
    FROM tbTransacciones t WITH (NOLOCK)
    JOIN cte_adm adm ON adm.unco_trnsccn = t.unco
    LEFT JOIN tbLogin lgn WITH (NOLOCK) ON lgn.unco = t.unco_lgn_rlza
    LEFT JOIN tbEstadosRegistros er WITH (NOLOCK) ON er.Unco = t.unco_estdo_rgstro
    LEFT JOIN cte_totales_trnsccn tt ON tt.unco_trnsccn = t.unco
    WHERE adm.cnsctvo_admsns = ? AND CAST(t.fcha_dcto AS DATE) >= CAST(? AS DATE) AND CAST(t.fcha_dcto AS DATE) <= CAST(? AS DATE)

    UNION ALL

    SELECT TOP (1)
        fa.cnsctvo_fctrcn                                  AS cnsctvo_dcto,
        LTRIM(RTRIM(ISNULL(t.dscrpcn_emprsa_crta, '')))    AS emprs,
        CONVERT(VARCHAR(10), fa.fcha_dcto, 23)             AS fcha_dcto,
        ISNULL(LTRIM(RTRIM(er.dscrpcn)), '')               AS estado,
        LTRIM(RTRIM(ISNULL(lgn.dscrpcn, '')))               AS usrio_realiza,
        ISNULL(t.nmro_idntfccn, '')                        AS nit,
        ISNULL(tf.total_fctra, 0)                          AS total_valor
    FROM tbFacturasAgrupadas fa WITH (NOLOCK)
    JOIN tbTransaccionesFacturasAgrupadas tfa WITH (NOLOCK) ON tfa.unco_fctra_agrpda = fa.unco
    JOIN tbTransacciones t WITH (NOLOCK) ON t.unco = tfa.unco_trnsccn
    JOIN cte_adm adm ON adm.unco_trnsccn = t.unco
    LEFT JOIN tbLogin lgn WITH (NOLOCK) ON lgn.unco = fa.unco_lgn_rlza
    LEFT JOIN tbEstadosRegistros er WITH (NOLOCK) ON er.Unco = fa.unco_estdo_rgstro
    LEFT JOIN cte_totales_fctra tf ON tf.unco = fa.unco
    WHERE adm.cnsctvo_admsns = ? AND CAST(fa.fcha_dcto AS DATE) >= CAST(? AS DATE) AND CAST(fa.fcha_dcto AS DATE) <= CAST(? AS DATE)
) resultado
"""

# Consulta para buscar por número de transacción (cnsctvo_dcto), usado en Consulta Externa.
# Retorna el cnsctvo_fctra_agrpda (factura agrupada asociada) si existe.
_CONSULTA_FACTURA_POR_TRANSACCION = """
WITH cte_totales_trnsccn AS (
    SELECT unco_trnsccn, ISNULL(SUM(total_detalle), 0) AS total_trnsccn
    FROM (
        SELECT ts.unco_trnsccn, CAST(ts.cntdd * ts.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesServicios ts WITH (NOLOCK)
        UNION ALL
        SELECT tsu.unco_trnsccn, CAST(tsu.cntdd * tsu.vlr_untro AS BIGINT) AS total_detalle
        FROM tbTransaccionesSuministros tsu WITH (NOLOCK)
    ) detalles
    GROUP BY unco_trnsccn
),
cte_fact_agrupada AS (
    SELECT tfa.unco_trnsccn, MAX(fa.cnsctvo_fctrcn) AS cnsctvo_fctrcn
    FROM tbTransaccionesFacturasAgrupadas tfa WITH (NOLOCK)
    JOIN tbFacturasAgrupadas fa WITH (NOLOCK) ON fa.unco = tfa.unco_fctra_agrpda
    GROUP BY tfa.unco_trnsccn
)
SELECT TOP (1)
    t.cnsctvo_dcto                                    AS cnsctvo_dcto,
    LTRIM(RTRIM(ISNULL(t.dscrpcn_emprsa_crta, '')))    AS emprs,
    CONVERT(VARCHAR(10), t.fcha_dcto, 23)              AS fcha_dcto,
    ISNULL(LTRIM(RTRIM(er.dscrpcn)), '')               AS estado,
    LTRIM(RTRIM(ISNULL(lgn.dscrpcn, '')))              AS usrio_realiza,
    ISNULL(t.nmro_idntfccn, '')                        AS nit,
    ISNULL(tt.total_trnsccn, 0)                        AS total_valor,
    ISNULL(fa.cnsctvo_fctrcn, 0)                       AS cnsctvo_fctra_agrpda
FROM tbTransacciones t WITH (NOLOCK)
LEFT JOIN tbLogin lgn WITH (NOLOCK) ON lgn.unco = t.unco_lgn_rlza
LEFT JOIN tbEstadosRegistros er WITH (NOLOCK) ON er.Unco = t.unco_estdo_rgstro
LEFT JOIN cte_totales_trnsccn tt ON tt.unco_trnsccn = t.unco
LEFT JOIN cte_fact_agrupada fa ON fa.unco_trnsccn = t.unco
WHERE t.cnsctvo_dcto = ? AND CAST(t.fcha_dcto AS DATE) >= CAST(? AS DATE) AND CAST(t.fcha_dcto AS DATE) <= CAST(? AS DATE)
ORDER BY t.fcha_dcto DESC
"""


class FacturaRepository:
    """Repositorio de información de facturas, relacionada a una subcarpeta a través del
    número de admisión (`[admision]`).
    """

    def __init__(self, conexion: SqlServerConnection | None = None) -> None:
        self._conexion = conexion or SqlServerConnection()

    def obtener_por_identificador(
        self,
        identificador: str,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        tipo_atencion: TipoAtencion | None = None,
    ) -> FacturaInfo | None:
        # Para Consulta Externa: buscar por número de transacción (cnsctvo_dcto)
        # Para otros tipos: buscar por número de admisión
        if tipo_atencion == TipoAtencion.CONSULTA_EXTERNA:
            return self._obtener_por_transaccion(identificador, fecha_desde, fecha_hasta)
        else:
            return self._obtener_por_admision(identificador, fecha_desde, fecha_hasta)

    def _obtener_por_admision(
        self, identificador: str, fecha_desde: date | None = None, fecha_hasta: date | None = None
    ) -> FacturaInfo | None:
        """Búsqueda por número de admisión (flujo por defecto para Urgencias)."""
        numero_admision = self._extraer_numero_admision(identificador)
        if numero_admision is None:
            logger.info("No se pudo interpretar '%s' como número de admisión.", identificador)
            return None

        # Rango de fechas: desde la fecha seleccionada hasta hoy.
        # Se envía como texto ISO: el driver ODBC "SQL Server" (legado) no soporta
        # bindear objetos date/datetime de Python (HYC00 - Optional feature not implemented).
        fecha_inicio = (fecha_desde or date(1900, 1, 1)).isoformat()
        fecha_fin = (fecha_hasta or date.today()).isoformat()
        try:
            with self._conexion.obtener_cursor() as cursor:
                cursor.execute(
                    _CONSULTA_FACTURA_POR_ADMISION,
                    (numero_admision, fecha_inicio, fecha_fin, numero_admision, fecha_inicio, fecha_fin),
                )
                fila = cursor.fetchone()
        except DatabaseError:
            logger.warning("No fue posible consultar la admisión %s.", numero_admision)
            return None

        if fila is None:
            return None

        cnsctvo_dcto, emprs, fcha_dcto, estado, usrio_realiza, nit, total_valor = fila
        numero_factura_str = str(cnsctvo_dcto).strip() if cnsctvo_dcto is not None else ""
        if numero_factura_str and not numero_factura_str.upper().startswith("SF"):
            numero_factura_str = f"SF{numero_factura_str}"

        return FacturaInfo(
            numero_factura=numero_factura_str,
            empresa=emprs or "",
            fecha_facturacion=fcha_dcto or "",
            estado=estado or "",
            usuario_factura=usrio_realiza or "",
            relacion_envio="",
            nit=nit or "",
            total=int(total_valor) if total_valor else 0,
        )

    def _obtener_por_transaccion(
        self, identificador: str, fecha_desde: date | None = None, fecha_hasta: date | None = None
    ) -> FacturaInfo | None:
        """Búsqueda por número de transacción (cnsctvo_dcto) para Consulta Externa.
        Retorna el cnsctvo_fctra_agrpda como número de factura si está disponible.
        """
        numero_transaccion = self._extraer_numero_transaccion(identificador)
        if numero_transaccion is None:
            logger.info("No se pudo interpretar '%s' como número de transacción.", identificador)
            return None

        fecha_inicio = (fecha_desde or date(1900, 1, 1)).isoformat()
        fecha_fin = (fecha_hasta or date.today()).isoformat()
        try:
            with self._conexion.obtener_cursor() as cursor:
                cursor.execute(
                    _CONSULTA_FACTURA_POR_TRANSACCION,
                    (numero_transaccion, fecha_inicio, fecha_fin),
                )
                fila = cursor.fetchone()
        except DatabaseError:
            logger.warning("No fue posible consultar la transacción %s.", numero_transaccion)
            return None

        if fila is None:
            return None

        cnsctvo_dcto, emprs, fcha_dcto, estado, usrio_realiza, nit, total_valor, cnsctvo_fctra_agrpda = fila
        # Usar cnsctvo_fctra_agrpda si está disponible; de lo contrario, usar cnsctvo_dcto
        numero_factura_valor = (
            cnsctvo_fctra_agrpda if cnsctvo_fctra_agrpda and cnsctvo_fctra_agrpda > 0 else cnsctvo_dcto
        )
        numero_factura_str = str(numero_factura_valor).strip() if numero_factura_valor is not None else ""
        if numero_factura_str and not numero_factura_str.upper().startswith("SF"):
            numero_factura_str = f"SF{numero_factura_str}"

        return FacturaInfo(
            numero_factura=numero_factura_str,
            empresa=emprs or "",
            fecha_facturacion=fcha_dcto or "",
            estado=estado or "",
            usuario_factura=usrio_realiza or "",
            relacion_envio="",
            nit=nit or "",
            total=int(total_valor) if total_valor else 0,
        )

    @staticmethod
    def _extraer_numero_admision(identificador: str) -> int | None:
        # Se asume que el nombre de la subcarpeta contiene el número de admisión (se
        # extraen solo los dígitos). TODO: ajustar si la convención real de nombres difiere.
        digitos = "".join(caracter for caracter in identificador if caracter.isdigit())
        return int(digitos) if digitos else None

    @staticmethod
    def _extraer_numero_transaccion(identificador: str) -> int | None:
        # Para Consulta Externa, el identificador es el cnsctvo_dcto (número de transacción).
        # Se extraen solo los dígitos del nombre de la carpeta.
        digitos = "".join(caracter for caracter in identificador if caracter.isdigit())
        return int(digitos) if digitos else None
