# Cambios Requeridos en el Notebook
## notebooks/proyecto_ia.ipynb

Este documento especifica los 4 cambios que deben aplicarse al notebook
para que sea ejecutable por colaboradores y en Google Colab.

Cada cambio indica qué celda modificar o dónde insertar una nueva celda.

---

## CAMBIO 1 — Reemplazar el contenido de la celda de configuración (celda 3)

**Buscar (cell-id: `cell-3`):**  
La celda que comienza con `ROOT = r'C:\Users\Felipe\...'`

**Reemplazar TODO el contenido de esa celda con:**

```python
# ── 0.2  Configuración ────────────────────────────────────────────────────────
import sys

# ── Detección de entorno ──────────────────────────────────────────────────────
IN_COLAB = 'google.colab' in sys.modules

# ── MODO DE EJECUCIÓN ─────────────────────────────────────────────────────────
# PARQUET_MODE = True   → carga data/processed/df_dataset.parquet (rápido)
#                         No requiere archivos DAT. Recomendado para colaboradores.
# PARQUET_MODE = False  → procesa archivos DAT desde cero (requiere ~9.3 GB)
#                         Solo si tienes acceso a la carpeta equipos/.
PARQUET_MODE = True   # ← cambiar a False solo si tienes los archivos DAT

# ── Rutas de proyecto ─────────────────────────────────────────────────────────
if IN_COLAB:
    # Ejecutar ANTES: from google.colab import drive; drive.mount('/content/drive')
    PROJ_ROOT = '/content/drive/MyDrive/compressor-project'   # ← ajustar al nombre de tu carpeta en Drive
else:
    # Ruta a la raíz del repositorio (un nivel por encima de notebooks/)
    PROJ_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))

# ── Ruta a los archivos DAT — solo necesaria si PARQUET_MODE = False ──────────
# Cambiar ROOT a la ruta local donde está la carpeta equipos/ en tu máquina
ROOT = r'C:\Users\Felipe\Desktop\Industrias\2026\IA\proyecto\equipos'

# ── Rutas de salida (siempre relativas al repositorio) ────────────────────────
FIG_DIR      = os.path.join(PROJ_ROOT, 'figures')
PARQUET_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'df_dataset.parquet')

# ── Construcción de rutas DAT — solo en modo completo ────────────────────────
if not PARQUET_MODE:
    _d1  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº1', 'CSDX165_INDNº1')
    _d2  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº2', 'CSDX165_INDNº2')
    _bf1 = 'BF_101803.1_1171_2026-05-27T09.48.42-04.00'
    _bf2 = 'BF_101803.2_1001_2026-05-27T09.54.00-04.00'
    _log1_dat = os.path.join(_d1, _bf1, 'reports_lang', 'CompressorMsgs.txt')
    _log2_dat = os.path.join(_d2, _bf2, 'reports_lang', 'CompressorMsgs.txt')
else:
    _d1 = _d2 = None
    _log1_dat = _log2_dat = None

# Los logs de eventos también están en data/events/ (para PARQUET_MODE y Colab)
_log1_repo = os.path.join(PROJ_ROOT, 'data', 'events', 'CompressorMsgs_INDNº1.txt')
_log2_repo = os.path.join(PROJ_ROOT, 'data', 'events', 'CompressorMsgs_INDNº2.txt')

COMPRESSORS = {
    'INDNº1': {
        'dat_root':    None if PARQUET_MODE else os.path.join(_d1, 'datarecorder'),
        'log_path':    _log1_repo if PARQUET_MODE else _log1_dat,
        'target_code': '0011',
        'target_cat':  'W',
        'dat_start':   datetime(2026, 3, 18),
        'dat_end':     datetime(2026, 5, 27),
    },
    'INDNº2': {
        'dat_root':    None if PARQUET_MODE else os.path.join(_d2, 'datarecorder'),
        'log_path':    _log2_repo if PARQUET_MODE else _log2_dat,
        'target_code': '0013',
        'target_cat':  'W',
        'dat_start':   datetime(2025, 6, 23),
        'dat_end':     datetime(2026, 5, 27),
    },
}

os.makedirs(FIG_DIR, exist_ok=True)

mode_str = 'PARQUET (rápido — sin DAT)' if PARQUET_MODE else 'DAT completo (~80 s)'
env_str  = 'Google Colab' if IN_COLAB else 'Jupyter local'
print(f'Entorno  : {env_str}')
print(f'Modo     : {mode_str}')
print(f'PROJ_ROOT: {PROJ_ROOT}')
if PARQUET_MODE:
    print(f'Parquet  : {PARQUET_PATH}')
print('Paths OK')
```

---

## CAMBIO 2 — Insertar celda de Quick-Start Loader

**Dónde insertar:** Después de la celda de definición de `compute_hours_loaded_since_clear`
(cell-id `cell-18`), antes de la sección de ensamblado del dataset (celda 19/20).

**Contenido de la nueva celda:**

```python
# ── QUICK-START: Cargar dataset desde Parquet (PARQUET_MODE = True) ───────────
#
# Si PARQUET_MODE = True, este bloque carga el dataset ya procesado y
# reconstruye las variables necesarias para los modelos y las figuras.
# Las celdas de procesamiento DAT (celdas 11, 15, 20) son omitidas.
#
# Si PARQUET_MODE = False, este bloque no hace nada — el pipeline DAT
# completo ya habrá construido df_dataset en las celdas anteriores.

if PARQUET_MODE:
    print('PARQUET_MODE activo — cargando dataset preprocesado...')

    # Verificar que el parquet existe
    if not os.path.isfile(PARQUET_PATH):
        raise FileNotFoundError(
            f'No se encontró {PARQUET_PATH}\n'
            'Opciones:\n'
            '  1. Descargar df_dataset.parquet y colocarlo en data/processed/\n'
            '  2. Cambiar PARQUET_MODE = False y tener acceso a los archivos DAT'
        )

    # Cargar dataset principal
    df_dataset = pd.read_parquet(PARQUET_PATH, engine='pyarrow')
    df_dataset.index = pd.to_datetime(df_dataset.index, utc=True).tz_localize(None)

    # Reconstruir subsets por compresor
    df_ind1 = df_dataset[df_dataset['compressor_id'] == 'INDNº1'].copy()
    df_ind2 = df_dataset[df_dataset['compressor_id'] == 'INDNº2'].copy()

    # Reconstruir features subsets (sin columnas de zonas/labels)
    zone_cols = ['zone', 'label_strict', 'label_extended', 'compressor_id']
    df_features_ind1 = df_ind1.drop(columns=[c for c in zone_cols if c in df_ind1.columns])
    df_features_ind2 = df_ind2.drop(columns=[c for c in zone_cols if c in df_ind2.columns])

    # Re-parsear eventos (necesario para Figura 2 — tabla de episodios)
    print('  Parseando logs de eventos para Figura 2...')
    df_ev_ind1 = parse_event_log(COMPRESSORS['INDNº1']['log_path'], '0011', 'W')
    df_ep_ind1 = build_episode_table(
        df_ev_ind1, COMPRESSORS['INDNº1']['dat_start'], COMPRESSORS['INDNº1']['dat_end'])

    df_ev_ind2 = parse_event_log(COMPRESSORS['INDNº2']['log_path'], '0013', 'W')
    df_ep_ind2 = build_episode_table(
        df_ev_ind2, COMPRESSORS['INDNº2']['dat_start'], COMPRESSORS['INDNº2']['dat_end'])

    # Labels separados (para compatibilidad con código posterior)
    df_labels_ind1 = df_ind1[['zone', 'label_strict', 'label_extended']]
    df_labels_ind2 = df_ind2[['zone', 'label_strict', 'label_extended']]

    FEAT_COLS = [c for c in MVP_FEATURE_COLS if c in df_dataset.columns]

    print(f'  df_dataset   : {df_dataset.shape}')
    print(f'  INDNº1 rows  : {len(df_ind1):,}   |   INDNº2 rows: {len(df_ind2):,}')
    print(f'  Episodios    : {len(df_ep_ind1)} (INDNº1)  +  {len(df_ep_ind2)} (INDNº2)')
    print(f'  FEAT_COLS    : {FEAT_COLS}')
    print('  Dataset listo. Continuar desde la sección de Modelos (celda siguiente).')
```

---

## CAMBIO 3 — Agregar guards a las celdas de procesamiento DAT pesado

**Tres celdas deben ser envueltas en `if not PARQUET_MODE:`**

### 3a — Celda de verificación Commit 1 (cell-id: `cell-11`)

Envolver TODO el contenido de la celda con:
```python
if not PARQUET_MODE:
    # [contenido original de la celda aquí]
    ...
else:
    print('PARQUET_MODE: verificación DAT omitida.')
```

### 3b — Celda de extracción de features (cell-id: `cell-15`)

Envolver TODO el contenido con:
```python
if not PARQUET_MODE:
    print('Extrayendo features  INDNº1 ...')
    _raw1 = extract_hourly_stats(COMPRESSORS['INDNº1']['dat_root'])
    df_features_ind1 = build_feature_matrix(_raw1, 'INDNº1')

    print('Extrayendo features  INDNº2 ...')
    _raw2 = extract_hourly_stats(COMPRESSORS['INDNº2']['dat_root'])
    df_features_ind2 = build_feature_matrix(_raw2, 'INDNº2')

    feat_cols_no_hls = [c for c in MVP_FEATURE_COLS if c != 'hours_loaded_since_clear']
    print(f'df_features_ind1 : {df_features_ind1.shape}')
    print(f'df_features_ind2 : {df_features_ind2.shape}')
else:
    print('PARQUET_MODE: extracción DAT omitida (datos cargados desde parquet).')
```

### 3c — Celda de ensamblado del dataset (cell-id: `cell-20`)

Envolver TODO el contenido con:
```python
if not PARQUET_MODE:
    # Re-parse events + episodes
    df_ev_ind1 = parse_event_log(COMPRESSORS['INDNº1']['log_path'], '0011', 'W')
    df_ep_ind1 = build_episode_table(
        df_ev_ind1, COMPRESSORS['INDNº1']['dat_start'], COMPRESSORS['INDNº1']['dat_end'])

    df_ev_ind2 = parse_event_log(COMPRESSORS['INDNº2']['log_path'], '0013', 'W')
    df_ep_ind2 = build_episode_table(
        df_ev_ind2, COMPRESSORS['INDNº2']['dat_start'], COMPRESSORS['INDNº2']['dat_end'])

    print('Ensamblando INDNº1 ...')
    df_ind1        = assemble_dataset(df_features_ind1, df_ep_ind1, df_ev_ind1)
    df_labels_ind1 = df_ind1[['zone', 'label_strict', 'label_extended']]

    print('Ensamblando INDNº2 ...')
    df_ind2        = assemble_dataset(df_features_ind2, df_ep_ind2, df_ev_ind2)
    df_labels_ind2 = df_ind2[['zone', 'label_strict', 'label_extended']]

    df_dataset = pd.concat([df_ind1, df_ind2]).sort_index()
    FEAT_COLS  = [c for c in MVP_FEATURE_COLS if c in df_dataset.columns]

    print(f'\ndf_ind1 : {df_ind1.shape}   df_ind2 : {df_ind2.shape}')
else:
    print('PARQUET_MODE: ensamblado omitido (df_dataset cargado desde parquet).')
```

---

## CAMBIO 4 — Agregar celda de exportación del dataset

**Dónde insertar:** Después de la celda de validaciones (cell-id: `cell-21`),
antes de la sección de modelos (markdown de celda 22).

**Contenido de la nueva celda:**

```python
# ── Exportar dataset a Parquet (ejecutar una sola vez — solo el autor) ────────
#
# Esta celda exporta df_dataset al archivo de reproducibilidad.
# Solo necesaria cuando PARQUET_MODE = False (pipeline DAT completo).
# El parquet generado permite a los colaboradores omitir el procesamiento DAT.

if not PARQUET_MODE:
    import os as _os
    _out_dir  = _os.path.join(PROJ_ROOT, 'data', 'processed')
    _out_path = _os.path.join(_out_dir, 'df_dataset.parquet')
    _os.makedirs(_out_dir, exist_ok=True)

    df_dataset.to_parquet(_out_path, engine='pyarrow', index=True)

    _size_mb = _os.path.getsize(_out_path) / 1024**2
    print(f'Dataset exportado : {_out_path}')
    print(f'Shape             : {df_dataset.shape}')
    print(f'Tamaño            : {_size_mb:.1f} MB')
    print(f'Columnas          : {list(df_dataset.columns)}')
    print()
    print('Compartir este archivo con colaboradores para que puedan')
    print('ejecutar el notebook con PARQUET_MODE = True.')
else:
    print('PARQUET_MODE activo — exportación omitida (el parquet ya existe).')
```

---

## Cómo copiar los archivos de eventos al repositorio

Después de aplicar los cambios anteriores, copiar los logs de eventos:

```
# Origen (en la carpeta equipos/ fuera del repo):
equipos\Compresor CSDX165 Aire Industrial Nº1\CSDX165_INDNº1\BF_101803.1_1171_...\reports_lang\CompressorMsgs.txt
equipos\Compresor CSDX165 Aire Industrial Nº2\CSDX165_INDNº2\BF_101803.2_1001_...\reports_lang\CompressorMsgs.txt

# Destino en el repositorio (renombrando):
data\events\CompressorMsgs_INDNº1.txt
data\events\CompressorMsgs_INDNº2.txt
```

En PowerShell:
```powershell
$base = "C:\Users\Felipe\Desktop\Industrias\2026\IA\proyecto"
$repo = "$base\compressor-predictive-maintenance"

Copy-Item "$base\equipos\Compresor CSDX165 Aire Industrial Nº1\CSDX165_INDNº1\BF_101803.1_1171_2026-05-27T09.48.42-04.00\reports_lang\CompressorMsgs.txt" `
          "$repo\data\events\CompressorMsgs_INDNº1.txt"

Copy-Item "$base\equipos\Compresor CSDX165 Aire Industrial Nº2\CSDX165_INDNº2\BF_101803.2_1001_2026-05-27T09.54.00-04.00\reports_lang\CompressorMsgs.txt" `
          "$repo\data\events\CompressorMsgs_INDNº2.txt"
```

---

## Orden de acciones para el autor (checklist)

```
[ ] 1. Aplicar los 4 cambios al notebook (este documento)
[ ] 2. Ejecutar el notebook con PARQUET_MODE = False y ROOT = ruta correcta
[ ] 3. Ejecutar la celda de exportación (Cambio 4) → genera df_dataset.parquet
[ ] 4. Verificar que el parquet se creó en data/processed/
[ ] 5. Copiar los archivos de eventos (ver comando PowerShell arriba)
[ ] 6. Cambiar PARQUET_MODE = True en el notebook
[ ] 7. Ejecutar Kernel → Restart & Run All para verificar que funciona sin DAT
[ ] 8. git add data/processed/df_dataset.parquet data/events/*.txt
[ ] 9. git commit -m "add reproducibility package: parquet dataset and event logs"
[ ] 10. git push
```
