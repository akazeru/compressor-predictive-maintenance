#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_notebook_changes.py - Apply 4 portability changes to proyecto_ia.ipynb
"""
import json, os, sys, shutil
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
NB_PATH   = os.path.join(REPO_ROOT, 'notebooks', 'proyecto_ia.ipynb')
BACKUP    = NB_PATH + f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'


def src(lines):
    out = []
    for i, line in enumerate(lines):
        out.append(line + '\n' if i < len(lines) - 1 else line)
    return out


def new_code_cell(lines):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [], "source": src(lines)}


def cell_starts_with(cell, text):
    s = cell.get('source', [])
    first = (s[0] if isinstance(s, list) and s else s)
    return isinstance(first, str) and first.startswith(text)


print(f'Loading {NB_PATH}')
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
shutil.copy2(NB_PATH, BACKUP)
print(f'Backup  -> {BACKUP}')
cells = nb['cells']


def find_by_start(text):
    for i, c in enumerate(cells):
        if cell_starts_with(c, text):
            return i
    return None


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 1: Replace path-config cell (starts with '# ── Rutas base')
# ─────────────────────────────────────────────────────────────────────────────
idx_c1 = find_by_start('# ── Rutas base')
if idx_c1 is None:
    print('ERROR: path-config cell not found'); sys.exit(1)

cells[idx_c1]['source'] = src([
    "# ── 0.2  Configuración ────────────────────────────────────────────",
    "import sys",
    "",
    "# ── Detección de entorno ────────────────────────────────────────────",
    "IN_COLAB = 'google.colab' in sys.modules",
    "",
    "# ── MODO DE EJECUCIÓN ─────────────────────────────────────────────",
    "# PARQUET_MODE = True   -> carga data/processed/df_dataset.parquet (rapido)",
    "#                          No requiere archivos DAT. Recomendado colaboradores.",
    "# PARQUET_MODE = False  -> procesa archivos DAT desde cero (~9.3 GB)",
    "PARQUET_MODE = False   # <- cambiar a True para colaboradores sin archivos DAT",
    "",
    "# ── Rutas de proyecto ────────────────────────────────────────────",
    "if IN_COLAB:",
    "    from google.colab import drive",
    "    drive.mount('/content/drive')",
    "    PROJ_ROOT = '/content/drive/MyDrive/compressor-project'   # <- ajustar",
    "else:",
    "    PROJ_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))",
    "",
    "# ── Ruta a los archivos DAT — solo necesaria si PARQUET_MODE = False ──────────",
    "ROOT = r'C:\\Users\\Felipe\\Desktop\\Industrias\\2026\\IA\\proyecto\\equipos'",
    "",
    "# ── Rutas derivadas ───────────────────────────────────────────────────",
    "FIG_DIR      = os.path.join(PROJ_ROOT, 'figures')",
    "PARQUET_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'df_dataset.parquet')",
    "",
    "if not PARQUET_MODE:",
    "    _d1  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº1', 'CSDX165_INDNº1')",
    "    _d2  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº2', 'CSDX165_INDNº2')",
    "    _bf1 = 'BF_101803.1_1171_2026-05-27T09.48.42-04.00'",
    "    _bf2 = 'BF_101803.2_1001_2026-05-27T09.54.00-04.00'",
    "    _log1_dat = os.path.join(_d1, _bf1, 'reports_lang', 'CompressorMsgs.txt')",
    "    _log2_dat = os.path.join(_d2, _bf2, 'reports_lang', 'CompressorMsgs.txt')",
    "else:",
    "    _d1 = _d2 = None",
    "    _log1_dat = _log2_dat = None",
    "",
    "_log1_repo = os.path.join(PROJ_ROOT, 'data', 'events', 'CompressorMsgs_INDNº1.txt')",
    "_log2_repo = os.path.join(PROJ_ROOT, 'data', 'events', 'CompressorMsgs_INDNº2.txt')",
    "",
    "COMPRESSORS = {",
    "    'INDNº1': {",
    "        'dat_root':    None if PARQUET_MODE else os.path.join(_d1, 'datarecorder'),",
    "        'log_path':    _log1_repo if PARQUET_MODE else _log1_dat,",
    "        'target_code': '0011',",
    "        'target_cat':  'W',",
    "        'dat_start':   datetime(2026, 3, 18),",
    "        'dat_end':     datetime(2026, 5, 27),",
    "    },",
    "    'INDNº2': {",
    "        'dat_root':    None if PARQUET_MODE else os.path.join(_d2, 'datarecorder'),",
    "        'log_path':    _log2_repo if PARQUET_MODE else _log2_dat,",
    "        'target_code': '0013',",
    "        'target_cat':  'W',",
    "        'dat_start':   datetime(2025, 6, 23),",
    "        'dat_end':     datetime(2026, 5, 27),",
    "    },",
    "}",
    "",
    "os.makedirs(FIG_DIR, exist_ok=True)",
    "",
    "mode_str = 'PARQUET (rapido)' if PARQUET_MODE else 'DAT completo'",
    "env_str  = 'Google Colab' if IN_COLAB else 'Jupyter local'",
    "print(f'Entorno  : {env_str}')",
    "print(f'Modo     : {mode_str}')",
    "print(f'PROJ_ROOT: {PROJ_ROOT}')",
    "if PARQUET_MODE:",
    "    print(f'Parquet  : {PARQUET_PATH}')",
    "print('Paths OK')",
])
print(f'Change 1 applied: path-config cell replaced (index {idx_c1})')


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 2: Insert Quick-Start Loader after compute_hours_loaded_since_clear
# ─────────────────────────────────────────────────────────────────────────────
idx_c18 = find_by_start('def compute_hours_loaded_since_clear')
if idx_c18 is None:
    print('ERROR: compute_hours_loaded_since_clear cell not found'); sys.exit(1)

qs_cell = new_code_cell([
    "# ── QUICK-START: Cargar dataset desde Parquet (PARQUET_MODE = True) ───────────",
    "# Si PARQUET_MODE = True: este bloque carga df_dataset y reconstruye variables.",
    "# Si PARQUET_MODE = False: no hace nada (pipeline DAT activo).",
    "",
    "if PARQUET_MODE:",
    "    print('PARQUET_MODE activo — cargando dataset preprocesado...')",
    "    if not os.path.isfile(PARQUET_PATH):",
    "        raise FileNotFoundError(",
    "            f'No se encontro {PARQUET_PATH}\\n'",
    "            'Opciones:\\n'",
    "            '  1. Colocar df_dataset.parquet en data/processed/\\n'",
    "            '  2. Cambiar PARQUET_MODE = False y tener acceso a los archivos DAT'",
    "        )",
    "    df_dataset = pd.read_parquet(PARQUET_PATH, engine='pyarrow')",
    "    df_dataset.index = pd.to_datetime(df_dataset.index)",
    "    df_ind1 = df_dataset[df_dataset['compressor_id'] == 'INDNº1'].copy()",
    "    df_ind2 = df_dataset[df_dataset['compressor_id'] == 'INDNº2'].copy()",
    "    _drop = ['zone', 'label_strict', 'label_extended', 'compressor_id']",
    "    df_features_ind1 = df_ind1.drop(columns=[c for c in _drop if c in df_ind1.columns])",
    "    df_features_ind2 = df_ind2.drop(columns=[c for c in _drop if c in df_ind2.columns])",
    "    print('  Parseando logs de eventos para Figura 2...')",
    "    df_ev_ind1 = parse_event_log(COMPRESSORS['INDNº1']['log_path'], '0011', 'W')",
    "    df_ep_ind1 = build_episode_table(",
    "        df_ev_ind1, COMPRESSORS['INDNº1']['dat_start'], COMPRESSORS['INDNº1']['dat_end'])",
    "    df_ev_ind2 = parse_event_log(COMPRESSORS['INDNº2']['log_path'], '0013', 'W')",
    "    df_ep_ind2 = build_episode_table(",
    "        df_ev_ind2, COMPRESSORS['INDNº2']['dat_start'], COMPRESSORS['INDNº2']['dat_end'])",
    "    df_labels_ind1 = df_ind1[['zone', 'label_strict', 'label_extended']]",
    "    df_labels_ind2 = df_ind2[['zone', 'label_strict', 'label_extended']]",
    "    FEAT_COLS = [c for c in MVP_FEATURE_COLS if c in df_dataset.columns]",
    "    print(f'  df_dataset   : {df_dataset.shape}')",
    "    print(f'  INDNº1 rows  : {len(df_ind1):,}   |   INDNº2 rows: {len(df_ind2):,}')",
    "    print(f'  Episodios    : {len(df_ep_ind1)} (INDNº1)  +  {len(df_ep_ind2)} (INDNº2)')",
    "    print(f'  FEAT_COLS    : {FEAT_COLS}')",
    "    print('  Dataset listo.')",
    "else:",
    "    print('PARQUET_MODE desactivado — continuando pipeline DAT.')",
])
cells.insert(idx_c18 + 1, qs_cell)
print(f'Change 2 applied: Quick-Start Loader inserted after index {idx_c18}')


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 3a: Wrap verification cell in PARQUET_MODE guard
# ─────────────────────────────────────────────────────────────────────────────
idx_c11 = find_by_start("SEP  = '=' * 70")
if idx_c11 is None:
    print('ERROR: verification cell not found'); sys.exit(1)

old_src = cells[idx_c11]['source']
indented = []
for line in old_src:
    if line in ('\n', ''):
        indented.append(line)
    else:
        indented.append('    ' + line)
new_src = (["if not PARQUET_MODE:\n"] + indented +
           ["\nelse:\n", "    print('PARQUET_MODE: verificacion DAT omitida.')"])
cells[idx_c11]['source'] = new_src
print(f'Change 3a applied: verification cell wrapped (index {idx_c11})')


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 3b: Replace extraction-run cell with guarded version
# ─────────────────────────────────────────────────────────────────────────────
idx_c15 = find_by_start("print('Extrayendo features  INDN")
if idx_c15 is None:
    print('ERROR: extraction-run cell not found'); sys.exit(1)

cells[idx_c15]['source'] = src([
    "if not PARQUET_MODE:",
    "    print('Extrayendo features  INDNº1 ...')",
    "    _raw1 = extract_hourly_stats(COMPRESSORS['INDNº1']['dat_root'])",
    "    df_features_ind1 = build_feature_matrix(_raw1, 'INDNº1')",
    "    print('Extrayendo features  INDNº2 ...')",
    "    _raw2 = extract_hourly_stats(COMPRESSORS['INDNº2']['dat_root'])",
    "    df_features_ind2 = build_feature_matrix(_raw2, 'INDNº2')",
    "    print(f'df_features_ind1 : {df_features_ind1.shape}')",
    "    print(f'df_features_ind2 : {df_features_ind2.shape}')",
    "else:",
    "    print('PARQUET_MODE: extraccion DAT omitida (datos desde parquet).')",
])
print(f'Change 3b applied: extraction-run cell replaced (index {idx_c15})')


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 3c: Replace assemble cell with guarded version
# ─────────────────────────────────────────────────────────────────────────────
idx_c20 = find_by_start('def assemble_dataset')
if idx_c20 is None:
    print('ERROR: assemble_dataset cell not found'); sys.exit(1)

cells[idx_c20]['source'] = src([
    "def assemble_dataset(df_features, df_episodes, df_events):",
    "    hls     = compute_hours_loaded_since_clear(df_features, df_events)",
    "    df_feat = df_features.copy()",
    "    df_feat['hours_loaded_since_clear'] = hls",
    "    df_lab  = assign_zones(df_feat, df_episodes)",
    "    return df_feat.join(df_lab, how='inner')",
    "",
    "",
    "if not PARQUET_MODE:",
    "    df_ev_ind1 = parse_event_log(COMPRESSORS['INDNº1']['log_path'], '0011', 'W')",
    "    df_ep_ind1 = build_episode_table(",
    "        df_ev_ind1, COMPRESSORS['INDNº1']['dat_start'], COMPRESSORS['INDNº1']['dat_end'])",
    "    df_ev_ind2 = parse_event_log(COMPRESSORS['INDNº2']['log_path'], '0013', 'W')",
    "    df_ep_ind2 = build_episode_table(",
    "        df_ev_ind2, COMPRESSORS['INDNº2']['dat_start'], COMPRESSORS['INDNº2']['dat_end'])",
    "    print('Ensamblando INDNº1 ...')",
    "    df_ind1        = assemble_dataset(df_features_ind1, df_ep_ind1, df_ev_ind1)",
    "    df_labels_ind1 = df_ind1[['zone', 'label_strict', 'label_extended']]",
    "    print('Ensamblando INDNº2 ...')",
    "    df_ind2        = assemble_dataset(df_features_ind2, df_ep_ind2, df_ev_ind2)",
    "    df_labels_ind2 = df_ind2[['zone', 'label_strict', 'label_extended']]",
    "    df_dataset = pd.concat([df_ind1, df_ind2]).sort_index()",
    "    FEAT_COLS  = [c for c in MVP_FEATURE_COLS if c in df_dataset.columns]",
    "    print(f'\\ndf_ind1 : {df_ind1.shape}   df_ind2 : {df_ind2.shape}')",
    "else:",
    "    print('PARQUET_MODE: ensamblado omitido (df_dataset desde parquet).')",
])
print(f'Change 3c applied: assemble cell replaced (index {idx_c20})')


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE 4: Insert export cell after combine+validation cell
# ─────────────────────────────────────────────────────────────────────────────
idx_c21 = find_by_start('# ── Combine both compressors')
if idx_c21 is None:
    print('ERROR: combine cell not found'); sys.exit(1)

export_cell = new_code_cell([
    "# ── Exportar dataset a Parquet (ejecutar una sola vez — solo el autor) ────────",
    "# Solo activa cuando PARQUET_MODE = False. Genera el archivo para colaboradores.",
    "",
    "if not PARQUET_MODE:",
    "    _out_dir  = os.path.join(PROJ_ROOT, 'data', 'processed')",
    "    _out_path = os.path.join(_out_dir, 'df_dataset.parquet')",
    "    os.makedirs(_out_dir, exist_ok=True)",
    "    df_dataset.to_parquet(_out_path, engine='pyarrow', index=True)",
    "    _size_mb = os.path.getsize(_out_path) / 1024**2",
    "    print(f'Parquet exportado : {_out_path}')",
    "    print(f'Shape             : {df_dataset.shape}')",
    "    print(f'Tamano            : {_size_mb:.1f} MB')",
    "    print(f'Columnas          : {list(df_dataset.columns)}')",
    "else:",
    "    print('PARQUET_MODE activo — exportacion omitida (parquet ya existe).')",
])
cells.insert(idx_c21 + 1, export_cell)
print(f'Change 4 applied: export cell inserted after index {idx_c21}')


# ── Save ──────────────────────────────────────────────────────────────────────
with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print()
print('=' * 60)
print('  All 4 changes applied successfully.')
print(f'  Saved: {NB_PATH}')
print('=' * 60)
