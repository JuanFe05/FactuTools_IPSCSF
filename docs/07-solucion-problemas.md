# Solución de problemas comunes

## 1. La app no conecta a la base de datos

Revisa en este orden:

1. **¿Está instalado el driver ODBC correcto en ese equipo?**
   ```powershell
   Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
   ```
   El nombre debe coincidir **exactamente** con `DB_DRIVER` en el `.env` (ej.
   `ODBC Driver 17 for SQL Server` o `ODBC Driver 18 for SQL Server`).

2. **¿Hay conectividad de red al servidor?**
   ```powershell
   Test-NetConnection -ComputerName <DB_SERVER> -Port 1433
   ```
   Si `TcpTestSucceeded` es `False`, es un problema de red/firewall, no de la app.

3. **¿El `.env` está en la carpeta correcta?** Debe estar junto al `.exe` (modo
   empaquetado) o en la raíz del proyecto (modo desarrollo) — ver
   [02-configuracion.md](02-configuracion.md).

4. **Revisa el log real** en `%LOCALAPPDATA%\FactuTools\logs\app.log`: el mensaje de
   error de `pyodbc` (capturado por `SqlServerConnection.obtener_cursor`) indica la causa
   exacta (credenciales inválidas, timeout, driver no encontrado, etc.).

## 2. "Installation of this product failed because it is not supported on this operating system" al instalar el ODBC Driver 17

El instalador de **ODBC Driver 17** es antiguo y rechaza instalarse en builds recientes
de Windows 10/11 aunque en la práctica serían compatibles. **Solución:** instalar
**ODBC Driver 18 for SQL Server** en su lugar (es el soportado actualmente por
Microsoft) y actualizar `DB_DRIVER=ODBC Driver 18 for SQL Server` en el `.env`. No hace
falta cambiar `DB_ENCRYPT`/`DB_TRUST_SERVER_CERTIFICATE`: la cadena de conexión fija esos
valores de forma explícita, así que no se ve afectada por el cambio de driver.

Descarga: [https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

## 3. La app se cierra sola / no abre ventana (modo desarrollo o empaquetado)

- Los errores de carga de QML van al **stderr de Qt**, no a la consola de Python ni al
  log; si no ves nada en `app.log`, puede ser un problema de QML (ruta de import, archivo
  faltante) en vez de una excepción de Python.
- Revisa igualmente `%LOCALAPPDATA%\FactuTools\logs\app.log`: cualquier excepción de
  Python no controlada queda ahí (ver `app/config/logging_config.py`).
- Si estás probando un `.exe` onefile recién compilado vía `Start-Process` +
  `Get-Process` en PowerShell: un onefile crea **dos procesos** (bootloader + proceso
  real) y puede tardar varios segundos en mostrar ventana. Verifica
  `MainWindowHandle`/`MainWindowTitle`, no solo si el proceso existe, antes de concluir
  que falló.

## 4. Modalidad CSV: "el CSV no tiene las columnas requeridas"

El archivo debe tener exactamente las columnas listadas en `COLUMNAS_REQUERIDAS` de
[app/services/csv/factura_csv_source.py](../app/services/csv/factura_csv_source.py).
Revisa que los encabezados coincidan (sin importar el orden) y que no falte ninguna.

## 5. Una subcarpeta no se renombra aunque "parece correcta"

El renombrado solo ocurre si **ambas** condiciones se cumplen:
- se encontró información de factura (en BD o CSV) para esa admisión, **y**
- la validación de soportes (`archivosCorrectos`) dio como resultado `Correcto`.

El motivo exacto (sin factura encontrada, o validación incorrecta) queda en el campo
`motivoError` de la fila, visible en el detalle de la tabla de resultados.

## 6. No se encuentran archivos FURIPS en la carpeta

`FuripsFileScanner` busca archivos **directamente dentro** de la carpeta seleccionada
(no en subcarpetas) cuyo nombre comience con `furips1` o `furips2` (sin distinguir
mayúsculas/minúsculas). Verifica que los archivos estén en el nivel correcto y que el
nombre empiece con ese prefijo.

## Dónde mirar siempre primero

```
%LOCALAPPDATA%\FactuTools\logs\app.log
```
Archivo rotativo (máx. 2 MB x 5 backups) con todo el logging de la app, incluidas las
excepciones no controladas. Es la fuente de verdad más rápida para diagnosticar
cualquier falla, tanto en desarrollo como en el ejecutable empaquetado.
