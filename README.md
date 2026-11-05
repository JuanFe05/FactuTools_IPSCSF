# FactuTools

Aplicación de escritorio (Windows) para la IPS Clínica Salud Florida que automatiza dos
tareas operativas de facturación en salud:

1. **Renombramiento de soportes**: valida y renombra los PDFs de soporte de cada admisión
   según las reglas de la EPS/empresa correspondiente, cruzando la información contra la
   base de datos del sistema de información (SQL Server) o contra un archivo CSV exportado.
2. **Separación de archivos FURIPS**: separa archivos planos FURIPS1/FURIPS2 (formato SOAT)
   en subcarpetas individuales por número de factura.

La interfaz está construida con **PySide6 + QML** y sigue una arquitectura por capas
(modelos, servicios, casos de uso, controladores) descrita en detalle en [docs/03-arquitectura.md](docs/03-arquitectura.md).

## Documentación

Toda la documentación detallada está organizada en la carpeta [docs/](docs/):

| Documento | Contenido |
|---|---|
| [docs/01-instalacion.md](docs/01-instalacion.md) | Requisitos y cómo correr la app en modo desarrollo |
| [docs/02-configuracion.md](docs/02-configuracion.md) | Variables de entorno (`.env`) y conexión a SQL Server |
| [docs/03-arquitectura.md](docs/03-arquitectura.md) | Estructura de carpetas y capas de la aplicación |
| [docs/04-funcionalidades.md](docs/04-funcionalidades.md) | Qué hace cada funcionalidad, paso a paso |
| [docs/05-empresas.md](docs/05-empresas.md) | Cómo están configuradas las reglas por empresa/EPS |
| [docs/06-empaquetado.md](docs/06-empaquetado.md) | Cómo generar el ejecutable (`.exe`) y distribuirlo |
| [docs/07-solucion-problemas.md](docs/07-solucion-problemas.md) | Errores comunes y cómo diagnosticarlos |

## Stack tecnológico

- Python 3.14, [PySide6](https://doc.qt.io/qtforpython/) (Qt Quick/QML) para la interfaz.
- `pyodbc` para la conexión a Microsoft SQL Server.
- `pandas` para el procesamiento de CSV.
- `pyinstaller` para empaquetar la app como ejecutable de Windows.
- Gestión de dependencias y entorno con [`uv`](https://docs.astral.sh/uv/).

## Inicio rápido

```powershell
uv sync
copy .env.example .env   # completar credenciales de BD
uv run main.py
```

Ver [docs/01-instalacion.md](docs/01-instalacion.md) para más detalle.
