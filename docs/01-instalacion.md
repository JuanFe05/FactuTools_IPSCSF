# Instalación y ejecución en modo desarrollo

## Requisitos previos

- **Windows** (la app usa rutas y convenciones específicas de Windows: `%LOCALAPPDATA%`,
  controlador ODBC de Microsoft, etc.).
- **Python 3.14** o superior.
- **[uv](https://docs.astral.sh/uv/)** instalado (gestor de entornos/dependencias usado
  en este proyecto; reemplaza a `pip`/`venv` manuales).
- **Microsoft ODBC Driver 17 o 18 for SQL Server** instalado, si vas a usar la modalidad
  de datos "Base de datos" (no es necesario si solo usarás la modalidad CSV en
  Renombramiento de soportes). Ver [07-solucion-problemas.md](07-solucion-problemas.md).
- Acceso de red al servidor SQL Server de la clínica (si aplica).

## Clonar e instalar dependencias

```powershell
git clone <url-del-repositorio>
cd FactuTools_IPSCSF
uv sync
```

`uv sync` crea el entorno virtual en `.venv/` e instala exactamente las versiones fijadas
en `uv.lock` (incluye PySide6, pyodbc, pandas, pyinstaller, etc. — ver [pyproject.toml](../pyproject.toml)).

## Configurar variables de entorno

```powershell
copy .env.example .env
```

Luego edita `.env` con los valores reales (servidor SQL, usuario, contraseña, etc.).
El detalle de cada variable está en [02-configuracion.md](02-configuracion.md).

> `.env` nunca debe subirse al repositorio (ya está en `.gitignore`); contiene credenciales.

## Ejecutar la aplicación

```powershell
uv run main.py
```

Esto abre la ventana principal (PySide6/QML). Si la ventana no abre o se cierra sola,
revisa el log en:
```
%LOCALAPPDATA%\FactuTools\logs\app.log
```
(los errores de QML van a stderr de Qt, no a la consola; el log de Python sí registra
excepciones no controladas — ver [07-solucion-problemas.md](07-solucion-problemas.md)).

## Activar el entorno manualmente (opcional)

Si prefieres no anteponer `uv run` a cada comando:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python main.py
```

## Siguiente paso

- Para entender qué hace cada funcionalidad: [04-funcionalidades.md](04-funcionalidades.md)
- Para generar un `.exe` distribuible: [06-empaquetado.md](06-empaquetado.md)
