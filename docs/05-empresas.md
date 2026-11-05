# Configuración de empresas/EPS (Renombramiento de soportes)

Las reglas de validación y renombrado por empresa **no se implementan como código por
empresa** (no hay una clase por EPS). Es un único validador genérico
(`ValidadorPorPrefijos`) parametrizado con datos (`EmpresaConfig`), siguiendo el principio
abierto/cerrado: agregar una EPS nueva es agregar una entrada de datos, sin tocar lógica
existente.

Todo vive en [app/services/empresas/](../app/services/empresas/):

| Archivo | Responsabilidad |
|---|---|
| `empresa_config.py` | Define `EmpresaConfig` (nombre, reglas por tipo de atención, prefijo de factura, si la carpeta incluye el NIT, nombres alternativos) y `ReglaSoportes` (prefijos obligatorios/alternativos/opcionales). |
| `registro_empresas.py` | Registro central (`_CONFIGS`): un diccionario `nombre empresa -> EmpresaConfig`. Es la fuente de la lista desplegable en la UI (`empresas_disponibles()`). |
| `validador_por_prefijos.py` | Única implementación de validación/renombrado: aplica las reglas de `EmpresaConfig` a los PDFs encontrados. |
| `validador_soportes.py` | Interfaz/contrato (`Protocol`) que implementa `ValidadorPorPrefijos`. |
| `normalizador.py` | Compara nombres de empresa de forma tolerante (mayúsculas, tildes, sufijos de régimen como "CONTRIBUTIVO"/"SUBSIDIADO"). |

## Cómo se definen los prefijos obligatorios

`ReglaSoportes` tiene tres listas:
- **`prefijos_obligatorios`**: todos deben estar presentes, o la validación falla.
- **`grupo_alternativo`**: basta con que al menos uno de estos prefijos esté presente
  (ej. `PDX` o `HEV` en Consulta Externa).
- **`prefijos_opcionales`**: se informan si están presentes, pero su ausencia nunca genera
  error.

El prefijo de cada PDF se extrae de las letras iniciales del nombre de archivo (ej.
`SF123.pdf` → prefijo `SF`; `FDE` se normaliza a `FE`).

## Ejemplo: agregar una empresa nueva

```python
# registro_empresas.py
_CONFIGS: dict[str, EmpresaConfig] = {
    # ...entradas existentes...
    "NUEVA EPS CONTRIBUTIVO": EmpresaConfig(
        nombre="NUEVA EPS CONTRIBUTIVO",
        reglas={
            TipoAtencion.CONSULTA_EXTERNA: _EXTERNA,  # reutiliza una regla existente
            TipoAtencion.URGENCIAS: ReglaSoportes(
                prefijos_obligatorios=("LDP", "CRC", "HEV", "SF"),
            ),
        },
        prefijo_factura="FEV",       # prefijo usado al renombrar (ej. FEV_<nit>_SF<factura>.pdf)
        carpeta_incluye_nit=False,   # si la carpeta final debe llevar el NIT de la IPS
        nombres_alternativos=(),     # variantes del nombre tal como aparecen en BD/CSV
    ),
}
```

No se requiere ningún otro cambio: la UI (`NuevoProcesoDialog.qml`) lee la lista desde
`empresas_disponibles()` automáticamente.

## Coincidencia de nombre de empresa (BD/CSV vs. selección del usuario)

`EmpresaConfig.coincide_con(nombre_en_datos)` centraliza la comparación: compara el
nombre principal y todos los `nombres_alternativos` contra el valor que viene de la base
de datos o del CSV, usando `normalizador.empresas_coinciden` (tolerante a mayúsculas,
tildes y variaciones de sufijo). Esto evita duplicar la lógica de comparación en cada
validador o fuente de datos.

## Nomenclatura de salida

Dado un PDF con prefijo `P` y una factura con número `N`:
- Si `P` es uno de `FE`, `FEV`, `FDE`, `FACTURA`, `SF` → se usa `prefijo_factura` de la
  empresa como tipo de documento.
- En otro caso, se conserva el prefijo detectado tal cual.
- Nombre final: `<tipo_documento>_<nit_ips>_SF<numero_factura>.pdf` (con sufijo `_2`,
  `_3`... si hay colisión de nombres dentro de la misma carpeta).
- Carpeta final: `SF<numero_factura>` (o `<nit_ips>_SF<numero_factura>` si
  `carpeta_incluye_nit=True`).
