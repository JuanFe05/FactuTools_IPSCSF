# Configuración (`.env`)

La app lee toda su configuración de un archivo `.env` (basado en
[.env.example](../.env.example)), usando [`python-dotenv`](https://pypi.org/project/python-dotenv/).
La carga ocurre en [app/config/settings.py](../app/config/settings.py).

**Dónde debe estar el `.env` según el modo de ejecución:**

| Modo | Ubicación esperada del `.env` |
|---|---|
| Desarrollo (`uv run main.py`) | Raíz del proyecto (junto a `main.py`) |
| Ejecutable empaquetado (`FactuTools.exe`) | **Misma carpeta** donde está el `.exe` |

Esto permite que cada equipo donde se instale el `.exe` tenga sus propias credenciales de
base de datos sin necesidad de recompilar (ver [06-empaquetado.md](06-empaquetado.md)).

## Variables disponibles

### Identidad de la app (se muestran en la UI vía `AppCtl`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `APP_NAME` | Nombre de la app (título de ventana, carpeta de logs en `%LOCALAPPDATA%`) | `FactuTools` |
| `APP_VERSION` | Versión mostrada en la UI y usada para comparar con GitHub Releases | `0.1.0` |
| `ORG_NAME` | Nombre de organización (`QGuiApplication.setOrganizationName`) | `IPS Clínica Salud Florida` |
| `CLINIC_NAME` | Nombre de la clínica mostrado en la UI | `IPS Clínica Salud Florida` |

### Entorno y logging

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `APP_ENV` | Etiqueta libre de entorno (`development`, `production`, etc.), informativa | `development` |
| `LOG_LEVEL` | Nivel de logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

Los logs se escriben (rotativos, máx. 2 MB x 5 archivos) en:
```
%LOCALAPPDATA%\<APP_NAME>\logs\app.log
```

### Actualizaciones automáticas

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `GITHUB_REPO` | Repositorio de GitHub en formato `owner/repo` usado para buscar nuevas versiones (releases). Si está vacío, la verificación de actualizaciones no hace nada. | *(vacío)* |

Ver [app/services/update/update_checker.py](../app/services/update/update_checker.py):
compara la última release de GitHub contra `APP_VERSION` (SemVer) y, si hay una más nueva
con un asset `.exe`, expone la URL de descarga.

### Conexión a Microsoft SQL Server

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DB_SERVER` | Host o IP del servidor SQL Server | *(vacío)* |
| `DB_PORT` | Puerto TCP | `1433` |
| `DB_NAME` | Nombre de la base de datos | *(vacío)* |
| `DB_USER` | Usuario SQL (autenticación SQL, no de Windows) | *(vacío)* |
| `DB_PASSWORD` | Contraseña del usuario SQL | *(vacío)* |
| `DB_DRIVER` | Nombre exacto del driver ODBC instalado en el equipo (ej. `ODBC Driver 17 for SQL Server` o `ODBC Driver 18 for SQL Server`) | `ODBC Driver 17 for SQL Server` |
| `DB_ENCRYPT` | Si la conexión debe cifrarse (`true`/`false`) | `true` |
| `DB_TRUST_SERVER_CERTIFICATE` | Si se confía en el certificado del servidor sin validarlo (útil con certificados autofirmados) | `false` |

Estas variables solo son obligatorias si vas a usar la modalidad **"Base de datos"** del
Renombramiento de soportes. La modalidad **"Archivo CSV"** no requiere conexión a SQL Server
en absoluto (ver [04-funcionalidades.md](04-funcionalidades.md)).

La cadena de conexión final se arma en `DatabaseSettings.connection_string()`
([app/config/settings.py](../app/config/settings.py)) y se usa en
[app/services/database/connection.py](../app/services/database/connection.py) vía `pyodbc`.

## Valores booleanos aceptados

Para `DB_ENCRYPT` y `DB_TRUST_SERVER_CERTIFICATE`, cualquiera de estos valores (sin
importar mayúsculas/minúsculas) se interpreta como verdadero: `1`, `true`, `yes`, `si`.
Cualquier otro valor (incluido vacío) se interpreta como falso.
