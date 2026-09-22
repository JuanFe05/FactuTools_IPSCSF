"""Escritura de los archivos FURIPS separados en subcarpetas por número de factura."""
from __future__ import annotations

from pathlib import Path

from app.models.furips import SplitTask

_OUTPUT_ENCODING = "utf-8"


class FuripsWriter:
    """Crea las carpetas y escribe los archivos de salida para cada `SplitTask`."""

    def write(self, base_folder: Path, task: SplitTask) -> Path:
        """Crea la subcarpeta ``base_folder / task.folder_id`` si no existe y escribe el
        archivo de salida con las líneas del task. Retorna la ruta del archivo creado."""
        output_dir = base_folder / task.folder_id
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / task.output_filename
        output_file.write_text("\n".join(task.lines), encoding=_OUTPUT_ENCODING)

        return output_file
