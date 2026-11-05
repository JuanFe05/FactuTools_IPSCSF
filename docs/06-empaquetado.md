# Generar y distribuir el ejecutable (.exe)

La app se empaqueta con [PyInstaller](https://pyinstaller.org/) a partir del spec
[factutools.spec](../factutools.spec) (raíz del proyecto).

## Generar el `.exe`

```powershell
uv run pyinstaller factutools.spec --noconfirm
```

Esto produce un único archivo portable:
```
dist/FactuTools.exe
```

- Modo **onefile** (todo empaquetado en un solo archivo) y **sin consola** (aplicación de
  escritorio).
- Incluye como datos empaquetados `app/views/qml/` (toda la interfaz) y
  `app/resources/images/` (logo), porque `main.py` las carga mediante
  `resource_path()` ([app/config/paths.py](../app/config/paths.py)), que resuelve
  `sys._MEIPASS` cuando corre empaquetado.
- `--noconfirm` evita la pregunta de sobrescribir `dist/FactuTools.exe` si ya existe.

Cada vez que cambias código (`.py` o `.qml`), debes **volver a ejecutar este comando**
para regenerar el `.exe` — no hay recarga automática en el ejecutable empaquetado.

### Carpetas generadas

| Carpeta | Qué es | ¿Se puede borrar? |
|---|---|---|
| `build/` | Archivos de trabajo intermedios de PyInstaller (análisis de dependencias, logs de advertencias). | Sí, en cualquier momento; se vuelve a generar en el próximo build. |
| `dist/` | Contiene el resultado final: `FactuTools.exe`. | Solo si ya no necesitas ese build. |

Ambas carpetas están en [.gitignore](../.gitignore) y no se versionan.

## Distribuir el `.exe` a otro equipo

El `.exe` **no lleva credenciales embebidas** (decisión deliberada, ver más abajo). Para
que funcione en otro equipo:

1. **Copiar `FactuTools.exe`** a la carpeta donde vivirá en ese equipo (ej. una carpeta
   compartida de red o el escritorio).
2. **Copiar un `.env`** (basado en [.env.example](../.env.example)) en la **misma
   carpeta** que el `.exe`, y completar ahí las credenciales de ese equipo/entorno
   (servidor SQL, usuario, contraseña — ver [02-configuracion.md](02-configuracion.md)).
   Cada equipo puede tener su propio `.env` con datos distintos, sin recompilar nada.
3. **Instalar el driver ODBC de SQL Server** en ese equipo si se va a usar la modalidad
   "Base de datos" (Microsoft ODBC Driver 17 o 18 for SQL Server). `pyodbc` no lo
   empaqueta: es un componente del sistema operativo, no una librería de Python. Ver
   [07-solucion-problemas.md](07-solucion-problemas.md) si la instalación falla.

> Al actualizar la versión del `.exe` en producción, basta con reemplazar
> `FactuTools.exe` por el nuevo build; el `.env` existente en esa carpeta no se toca.

## Por qué el `.env` vive fuera del binario

`app/config/settings.py` detecta si corre empaquetado (`sys.frozen`) y, en ese caso, busca
el `.env` junto al ejecutable (`Path(sys.executable).resolve().parent`) en vez de dentro
del paquete de PyInstaller. Esto evita tener que **hornear contraseñas de base de datos
dentro del binario** (que quedarían visibles para cualquiera que inspeccione el `.exe`) y
permite reutilizar el mismo `.exe` en varios equipos con configuraciones distintas.

## Verificación rápida tras compilar

```powershell
Start-Process "dist\FactuTools.exe"
```

Si la ventana no aparece o se cierra sola, revisa:
- `%LOCALAPPDATA%\FactuTools\logs\app.log` en el equipo donde corriste el `.exe`
  (ahí quedan registradas las excepciones de Python no controladas).
- Que el `.env` esté realmente en la misma carpeta que el `.exe`.
- Que el driver ODBC esté instalado (si usas la modalidad "Base de datos").

Nota para quien compile usando Start-Process/Get-Process en PowerShell para probar: un
`.exe` onefile crea **dos procesos** con el mismo nombre (el bootloader que se
autoextrae y el proceso real), y tarda unos segundos en abrir ventana la primera vez.
Verifica `MainWindowHandle`/`MainWindowTitle` del proceso, no solo si el proceso existe,
para confirmar que realmente abrió una ventana visible.
