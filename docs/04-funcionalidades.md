# Funcionalidades

La app tiene dos funcionalidades independientes, accesibles desde la barra lateral
(`Sidebar.qml`).

---

## 1. Renombramiento de soportes

**Objetivo:** validar que cada admisión tenga los soportes PDF obligatorios según la
empresa/EPS y el tipo de atención, y renombrar tanto los PDFs como la carpeta de la
admisión siguiendo la nomenclatura exigida para el envío a la EPS.

### Datos de entrada que pide al usuario

1. **Carpeta principal**: la carpeta que contiene, como subcarpetas directas, una carpeta
   por admisión (cada una con sus PDFs de soporte).
2. **Empresa/EPS**: lista fija de empresas configuradas (ver
   [05-empresas.md](05-empresas.md)).
3. **Tipo de atención**: `Consulta Externa` o `Urgencias` (determina qué prefijos de PDF
   son obligatorios).
4. **Origen del dato de factura** — dos modalidades mutuamente excluyentes:
   - **Base de datos**: requiere `Fecha desde` (rango de búsqueda) y conexión configurada
     a SQL Server (ver [02-configuracion.md](02-configuracion.md)).
   - **Archivo CSV**: requiere seleccionar un `.csv` exportado del sistema de información,
     con las columnas exactas definidas en
     [app/services/csv/factura_csv_source.py](../app/services/csv/factura_csv_source.py)
     (`COLUMNAS_REQUERIDAS`). En esta modalidad el tipo de atención queda fijo en
     `Urgencias` y no se pide fecha.

### Flujo paso a paso

1. Al seleccionar la carpeta, la app hace un escaneo rápido (cuenta subcarpetas y PDFs) —
   `app/services/processors/carpeta_scanner.py`.
2. **Analizar** (botón): por cada subcarpeta,
   - extrae el número de admisión del nombre de la carpeta (solo dígitos),
   - busca la factura asociada (en BD o en el CSV, según la modalidad),
   - valida los PDFs presentes contra las reglas de la empresa seleccionada
     (`ValidadorPorPrefijos.validar`),
   - muestra el resultado en una tabla: factura encontrada o no, soportes correctos o no,
     empresa, fecha de facturación, estado, usuario, total.
3. **Renombrar** (botón, se habilita solo si el análisis no tiene errores críticos):
   repite el mismo análisis y, para cada subcarpeta con factura encontrada y validación
   correcta:
   - renombra cada PDF a `<TIPO_DOCUMENTO>_<NIT_IPS>_SF<NUMERO_FACTURA>.pdf` (con
     numeración `_2`, `_3`... si hay nombres repetidos),
   - renombra la carpeta de la admisión a `SF<NUMERO_FACTURA>` (o
     `<NIT_IPS>_SF<NUMERO_FACTURA>` si la empresa lo requiere).
4. **Borrar todo**: limpia el estado (carpeta, empresa, resultados) para iniciar un
   proceso nuevo.

### Validaciones y manejo de errores

- Si no se encuentra la factura (BD o CSV), la subcarpeta queda marcada como
  "no encontrada" y no se renombra.
- Si la empresa de la factura no coincide con la seleccionada, o faltan prefijos de PDF
  obligatorios, la validación marca la subcarpeta como incorrecta (detalle visible en la
  tabla) y tampoco se renombra.
- Errores de sistema de archivos al renombrar (ej. archivo en uso, carpeta destino ya
  existente) se capturan por subcarpeta y no detienen el proceso completo.

### Dato técnico: consulta a base de datos

`FacturaRepository` ([app/repositories/factura_repository.py](../app/repositories/factura_repository.py))
ejecuta una consulta SQL propia y acotada (no la consulta de reporte completa del
sistema) que resuelve, a partir del número de admisión y un rango de fechas: número de
factura, empresa, fecha de facturación, estado, usuario, NIT y total (sumando todos los
`cntdd1 * vlr_untro` del documento).

---

## 2. Separación de archivos FURIPS

**Objetivo:** tomar los archivos planos `FURIPS1`/`FURIPS2` (formato de reporte SOAT) que
contienen líneas de **varias facturas mezcladas**, y separarlos en un archivo por factura,
organizados en subcarpetas.

### Datos de entrada que pide al usuario

- **Carpeta principal**: debe contener directamente los archivos `FURIPS1*.txt` y/o
  `FURIPS2*.txt` a procesar (la detección es por prefijo del nombre de archivo, sin
  distinguir mayúsculas/minúsculas).

### Flujo paso a paso

1. Al seleccionar la carpeta, se cuentan los archivos FURIPS encontrados
   (`FuripsFileScanner.scan`).
2. **Analizar**: parsea cada archivo (`FuripsParserFactory` — Strategy por prefijo),
   agrupa las líneas por número de factura (`folder_id`) y muestra en una tabla, por
   factura: si se generará `FURIPS1`, si se generará `FURIPS2`.
3. **Separar** (botón, se habilita solo si hay archivos FURIPS detectados y sin errores
   previos): repite el mismo análisis y, por cada factura, crea una subcarpeta
   `<carpeta_principal>/<numero_factura>/` y escribe dentro los archivos
   `FURIPS1_<numero_factura>.txt` y/o `FURIPS2_<numero_factura>.txt` con las líneas
   correspondientes (`FuripsWriter.write`).
4. **Borrar todo**: limpia el estado para iniciar un proceso nuevo.

### Manejo de errores

- Si la carpeta no contiene archivos `FURIPS1`/`FURIPS2`, se informa como error previo y
  el botón "Separar" permanece deshabilitado.
- Errores de escritura (permisos, disco, etc.) se capturan por factura sin detener el
  resto del proceso; la factura queda marcada con el error puntual en la tabla.

---

## Progreso y ejecución en segundo plano

Ambas funcionalidades ejecutan su lógica en un `QThread` dedicado
([app/controllers/workers.py](../app/controllers/workers.py)), reportando progreso
(`actual`, `total`, `mensaje`) a la interfaz sin bloquearla. Al finalizar, se muestra un
diálogo de resultado con el resumen agregado (`a_resumen()` del modelo correspondiente).
