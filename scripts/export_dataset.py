"""
export_dataset.py
=================
Script de exportación del dataset procesado a formato Parquet.

Ejecutar DESPUÉS de correr el notebook con PARQUET_MODE = False
(el notebook debe haber generado df_dataset en memoria).

Uso alternativo: correr este script directamente si el notebook ya ejecutó
la sección de ensamblado del dataset en la misma sesión del kernel.

INSTRUCCIONES
-------------
Este script es para uso del autor (quien tiene acceso a los archivos DAT).
Los colaboradores deben usar df_dataset.parquet ya generado (data/processed/).

Para exportar el dataset:
  1. Abrir notebooks/proyecto_ia.ipynb en Jupyter
  2. Configurar PARQUET_MODE = False y ROOT = <ruta a equipos/>
  3. Ejecutar todas las celdas hasta la sección de modelos (celda 21 inclusive)
  4. Abrir una terminal en la raíz del repositorio y ejecutar:
       python scripts/export_dataset.py

El script asume que el kernel de Jupyter está activo y que df_dataset
ya fue definido. Si no, ejecutar directamente desde el notebook.
"""

import os
import sys

# ── Intentar importar pandas y pyarrow ────────────────────────────────────────
try:
    import pandas as pd
except ImportError:
    sys.exit("Error: pandas no está instalado. Ejecutar: pip install pandas")

try:
    import pyarrow  # noqa: F401
except ImportError:
    sys.exit("Error: pyarrow no está instalado. Ejecutar: pip install pyarrow")

# ── Ruta de salida ─────────────────────────────────────────────────────────────
REPO_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR  = os.path.join(REPO_ROOT, 'data', 'processed')
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'df_dataset.parquet')

# ── Código de exportación (pegar en celda del notebook si se prefiere) ─────────
EXPORT_CELL_CODE = '''
# ── Exportar dataset a Parquet ─────────────────────────────────────────────────
import os
PARQUET_EXPORT_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'df_dataset.parquet')
os.makedirs(os.path.dirname(PARQUET_EXPORT_PATH), exist_ok=True)
df_dataset.to_parquet(PARQUET_EXPORT_PATH, engine='pyarrow', index=True)
print(f"Dataset exportado: {PARQUET_EXPORT_PATH}")
print(f"Shape: {df_dataset.shape}")
print(f"Tamaño: {os.path.getsize(PARQUET_EXPORT_PATH) / 1024**2:.1f} MB")
print(f"Columnas: {list(df_dataset.columns)}")
'''

def main():
    print("=" * 60)
    print("  EXPORTACIÓN DEL DATASET A PARQUET")
    print("=" * 60)
    print()
    print("Este script no puede ejecutar el notebook directamente.")
    print()
    print("Para exportar el dataset, agrega la siguiente celda")
    print("al final de la sección de Dataset en el notebook")
    print("(después de la celda de validación, sección 5):")
    print()
    print("-" * 60)
    print(EXPORT_CELL_CODE)
    print("-" * 60)
    print()
    print(f"El archivo se guardará en:")
    print(f"  {OUTPUT_PATH}")
    print()
    print("También puedes copiar el código de arriba directamente")
    print("a una celda del notebook y ejecutarla.")


def export_from_dataframe(df_dataset, proj_root=None):
    """
    Exportar df_dataset a Parquet.
    Llamar desde el notebook con: export_from_dataframe(df_dataset, PROJ_ROOT)

    Ejemplo de uso en el notebook:
        import sys
        sys.path.insert(0, '../scripts')
        from export_dataset import export_from_dataframe
        export_from_dataframe(df_dataset, PROJ_ROOT)
    """
    if proj_root is None:
        proj_root = REPO_ROOT

    output_dir  = os.path.join(proj_root, 'data', 'processed')
    output_path = os.path.join(output_dir, 'df_dataset.parquet')

    os.makedirs(output_dir, exist_ok=True)
    df_dataset.to_parquet(output_path, engine='pyarrow', index=True)

    size_mb = os.path.getsize(output_path) / 1024**2
    print(f"Exportado: {output_path}")
    print(f"Shape    : {df_dataset.shape}")
    print(f"Tamaño   : {size_mb:.1f} MB")
    print(f"Columnas : {list(df_dataset.columns)}")
    return output_path


if __name__ == '__main__':
    main()
