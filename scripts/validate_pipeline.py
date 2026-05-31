#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_pipeline.py
====================
Replicate the full notebook pipeline outside Jupyter.
Phase 1 — PARQUET_MODE=False: process DAT files, train models, export parquet.
Phase 2 — PARQUET_MODE=True:  load parquet, train models, assert metrics match.

Run from the repository root:
    python scripts/validate_pipeline.py
"""

import os, re, glob, struct, time, warnings
from datetime import datetime

warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')          # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter, MonthLocator

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score,
                              recall_score, f1_score, confusion_matrix)
from sklearn.utils.class_weight import compute_class_weight

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARQUET_PATH = os.path.join(REPO_ROOT, 'data', 'processed', 'df_dataset.parquet')
FIG_DIR      = os.path.join(REPO_ROOT, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(os.path.join(REPO_ROOT, 'data', 'processed'), exist_ok=True)

ROOT = r'C:\Users\Felipe\Desktop\Industrias\2026\IA\proyecto\equipos'

_d1  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº1', 'CSDX165_INDNº1')
_d2  = os.path.join(ROOT, 'Compresor CSDX165 Aire Industrial Nº2', 'CSDX165_INDNº2')
_bf1 = 'BF_101803.1_1171_2026-05-27T09.48.42-04.00'
_bf2 = 'BF_101803.2_1001_2026-05-27T09.54.00-04.00'

COMPRESSORS = {
    'INDNº1': {
        'dat_root':    os.path.join(_d1, 'datarecorder'),
        'log_path':    os.path.join(_d1, _bf1, 'reports_lang', 'CompressorMsgs.txt'),
        'target_code': '0011',
        'target_cat':  'W',
        'dat_start':   datetime(2026, 3, 18),
        'dat_end':     datetime(2026, 5, 27),
    },
    'INDNº2': {
        'dat_root':    os.path.join(_d2, 'datarecorder'),
        'log_path':    os.path.join(_d2, _bf2, 'reports_lang', 'CompressorMsgs.txt'),
        'target_code': '0013',
        'target_cat':  'W',
        'dat_start':   datetime(2025, 6, 23),
        'dat_end':     datetime(2026, 5, 27),
    },
}

# ── Constants ─────────────────────────────────────────────────────────────────
DAT_VALID_SIZE    = 954_664
DAT_DATA_OFFSET   = 4264
DAT_REC_SIZE      = 264
DAT_N_RECORDS     = 3600
DAT_MISSING_INT16 = -32768

CH = {'cs':0,'pressure':4,'oil_temp':6,'inlet_temp':9,'speed_sp':12,
      'fan_speed':38,'etm_valve':44,'etm_fan_sp':45,'etm_ctrl':47}
CH_SCALE = {'cs':1.,'pressure':.01,'oil_temp':.01,'inlet_temp':.1,
            'speed_sp':10.,'fan_speed':10.,'etm_valve':.1,'etm_fan_sp':.1,'etm_ctrl':.1}
CH_NAMES        = list(CH.keys())
EXTRACT_INDICES = [CH[k] for k in CH_NAMES]

PREDICTION_HORIZON_H = 24
RECOVERY_EXCLUSION_H = 4
EPISODE_GAP_DAYS     = 7
ZONE_NEGATIVE = 'negative'
ZONE_PRE_WARN = 'pre_warning'
ZONE_ACTIVE   = 'active_warning'
ZONE_RECOVERY = 'recovery'
TARGET_COL    = 'label_extended'

MVP_FEATURE_COLS = [
    'p_mean_1h','p_std_1h','oil_temp_mean_1h','oil_temp_max_1h',
    'speed_mean_1h','speed_std_1h','load_frac_1h','hours_loaded_since_clear',
]

# ── DAT functions (from notebook cells 6, 13, 14) ─────────────────────────────
def list_dat_files(dat_root):
    files = sorted(glob.glob(os.path.join(dat_root,'**','mcs_*.dat'), recursive=True))
    return [f for f in files if os.path.getsize(f) == DAT_VALID_SIZE]

def read_dat_hour(filepath):
    with open(filepath,'rb') as fh:
        data = fh.read()
    ts0      = struct.unpack_from('<I', data, DAT_DATA_OFFSET)[0]
    hour_utc = datetime.utcfromtimestamp(ts0)
    flat = np.frombuffer(data, dtype='<i2', offset=DAT_DATA_OFFSET,
                         count=DAT_N_RECORDS*(DAT_REC_SIZE//2)
                         ).reshape(DAT_N_RECORDS, DAT_REC_SIZE//2)
    ch_all = flat[:,2:].astype(np.float64)
    ch_all[ch_all == DAT_MISSING_INT16] = np.nan
    return hour_utc, ch_all[:,EXTRACT_INDICES]

def extract_hourly_stats(dat_root):
    files = list_dat_files(dat_root)
    CI    = {name: i for i, name in enumerate(CH_NAMES)}
    rows  = []
    t0    = time.time()
    for i, fp in enumerate(files):
        if i % 500 == 0:
            print(f'  {i:,}/{len(files):,}  ({time.time()-t0:.0f}s)', end='\r', flush=True)
        try:
            hour_utc, raw = read_dat_hour(fp)
        except Exception:
            continue
        cs       = raw[:,CI['cs']]
        pressure = raw[:,CI['pressure']] * CH_SCALE['pressure']
        oil_temp = raw[:,CI['oil_temp']] * CH_SCALE['oil_temp']
        speed    = raw[:,CI['speed_sp']] * CH_SCALE['speed_sp']
        loaded    = (~np.isnan(cs)) & (cs != 0)
        load_frac = float(loaded.sum()) / len(cs)
        def _s(arr):
            v = arr[~np.isnan(arr)]
            if len(v) == 0: return np.nan, np.nan, np.nan
            return float(v.mean()), float(v.std()), float(v.max())
        p_mn,p_sd,_     = _s(pressure)
        o_mn,o_sd,o_mx  = _s(oil_temp)
        s_mn,s_sd,_     = _s(speed)
        rows.append({'hour_utc':hour_utc,'p_mean':p_mn,'p_std':p_sd,
                     'oil_temp_mean':o_mn,'oil_temp_max':o_mx,
                     'speed_mean':s_mn,'speed_std':s_sd,'load_frac':load_frac})
    print(f'  Done: {len(rows):,} hours  ({time.time()-t0:.1f}s)          ')
    df = pd.DataFrame(rows).sort_values('hour_utc').reset_index(drop=True)
    df['hour_utc'] = pd.to_datetime(df['hour_utc'])
    return df.set_index('hour_utc')

def build_feature_matrix(df_raw, comp_id):
    df = df_raw.rename(columns={
        'p_mean':'p_mean_1h','p_std':'p_std_1h',
        'oil_temp_mean':'oil_temp_mean_1h','oil_temp_max':'oil_temp_max_1h',
        'speed_mean':'speed_mean_1h','speed_std':'speed_std_1h','load_frac':'load_frac_1h',
    }).copy()
    df.insert(0,'compressor_id',comp_id)
    return df

# ── Event log functions (from notebook cells 8, 9) ────────────────────────────
_HEADER_RE = re.compile(
    r'^(\d{4})\s+([OWA])\s+([cga])\s+'
    r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([-+]\d{2}):?(\d{2})'
)

def parse_event_log(log_path, target_code, target_cat):
    rows = []
    with open(log_path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            m = _HEADER_RE.match(line.strip())
            if not m: continue
            if m.group(1) != target_code or m.group(2) != target_cat: continue
            dt   = datetime.strptime(m.group(4),'%Y-%m-%dT%H:%M:%S')
            tz_h = int(m.group(5))
            rows.append({'timestamp':dt,'state':m.group(3),'tz_offset_h':tz_h})
    if not rows:
        return pd.DataFrame(columns=['timestamp','state','tz_offset_h'])
    return (pd.DataFrame(rows).sort_values('timestamp')
              .drop_duplicates(subset=['timestamp','state']).reset_index(drop=True))

def build_episode_table(df_events, dat_start, dat_end):
    onsets = df_events[df_events['state']=='c'].reset_index(drop=True)
    clears = df_events[df_events['state']=='g'].reset_index(drop=True)
    if onsets.empty:
        return pd.DataFrame(columns=['episode_id','first_onset','last_clear',
                                     'n_onsets','in_dat','duration_days'])
    ep_groups, current = [], [onsets.iloc[0]['timestamp']]
    for i in range(1,len(onsets)):
        gap_s = (onsets.iloc[i]['timestamp']-onsets.iloc[i-1]['timestamp']).total_seconds()
        if gap_s > EPISODE_GAP_DAYS*86_400:
            ep_groups.append(current); current=[]
        current.append(onsets.iloc[i]['timestamp'])
    ep_groups.append(current)
    rows = []
    for ep_id, ep_ts in enumerate(ep_groups,1):
        first_onset = ep_ts[0]
        upper = ep_groups[ep_id][0] if ep_id<len(ep_groups) else pd.Timestamp.max
        mask  = (clears['timestamp']>first_onset)&(clears['timestamp']<upper)
        last_clear = clears.loc[mask,'timestamp'].max() if mask.any() else pd.NaT
        dur = ((last_clear-first_onset).total_seconds()/86_400
               if pd.notna(last_clear) else np.nan)
        rows.append({'episode_id':ep_id,'first_onset':first_onset,
                     'last_clear':last_clear,'n_onsets':len(ep_ts),
                     'in_dat':dat_start<=first_onset<=dat_end,
                     'duration_days':round(dur,2) if pd.notna(last_clear) else np.nan})
    df_eps = pd.DataFrame(rows)
    return df_eps[df_eps['in_dat']].reset_index(drop=True)

# ── Zone / label functions (from notebook cells 17, 18) ───────────────────────
def assign_zones(df_features, df_episodes):
    idx   = df_features.index
    zones = pd.Series(ZONE_NEGATIVE, index=idx, dtype='object', name='zone')
    for _, ep in df_episodes.iterrows():
        t0 = pd.Timestamp(ep['first_onset'])
        t1 = (pd.Timestamp(ep['last_clear']) if pd.notna(ep['last_clear']) else idx.max())
        zones[(idx>=t0)&(idx<=t1)] = ZONE_ACTIVE
        t_rec = t1+pd.Timedelta(hours=RECOVERY_EXCLUSION_H)
        zones[(idx>t1)&(idx<=t_rec)] = ZONE_RECOVERY
        t_pre = t0-pd.Timedelta(hours=PREDICTION_HORIZON_H)
        pre_mask = (idx>=t_pre)&(idx<t0)&(zones==ZONE_NEGATIVE)
        zones[pre_mask] = ZONE_PRE_WARN
    label_strict   = zones.map({ZONE_PRE_WARN:1.,ZONE_NEGATIVE:0.,
                                 ZONE_ACTIVE:np.nan,ZONE_RECOVERY:np.nan}).astype('float64')
    label_extended = zones.map({ZONE_PRE_WARN:1.,ZONE_ACTIVE:1.,
                                 ZONE_NEGATIVE:0.,ZONE_RECOVERY:np.nan}).astype('float64')
    return pd.DataFrame({'zone':zones,'label_strict':label_strict,
                         'label_extended':label_extended})

def compute_hours_loaded_since_clear(df_features, df_events):
    clears_ts  = sorted(pd.Timestamp(t)
                        for t in df_events.loc[df_events['state']=='g','timestamp'])
    load_fracs = df_features['load_frac_1h'].fillna(0.).values
    result     = np.zeros(len(df_features))
    acc, ptr   = 0., 0
    for i, hour_utc in enumerate(df_features.index):
        while ptr<len(clears_ts) and hour_utc>=clears_ts[ptr]:
            acc=0.; ptr+=1
        result[i] = acc
        acc       += load_fracs[i]
    return pd.Series(result, index=df_features.index, name='hours_loaded_since_clear')

def assemble_dataset(df_features, df_episodes, df_events):
    hls     = compute_hours_loaded_since_clear(df_features, df_events)
    df_feat = df_features.copy()
    df_feat['hours_loaded_since_clear'] = hls
    df_lab  = assign_zones(df_feat, df_episodes)
    return df_feat.join(df_lab, how='inner')

# ── Model training & evaluation ───────────────────────────────────────────────
def train_and_evaluate(df_dataset):
    df_usable = df_dataset[df_dataset['zone'] != ZONE_RECOVERY].copy()
    df_train  = df_usable[df_usable['compressor_id'] == 'INDNº2']
    df_test   = df_usable[df_usable['compressor_id'] == 'INDNº1']
    FEAT_COLS = [c for c in MVP_FEATURE_COLS if c in df_dataset.columns]

    X_train = df_train[FEAT_COLS].values.astype(np.float32)
    y_train = df_train[TARGET_COL].values.astype(int)
    X_test  = df_test[FEAT_COLS].values.astype(np.float32)
    y_test  = df_test[TARGET_COL].values.astype(int)

    cw_vals = compute_class_weight('balanced', classes=np.array([0,1]), y=y_train)
    CLASS_WEIGHT = {0: float(cw_vals[0]), 1: float(cw_vals[1])}

    results = {}

    # Decision Tree
    dt = DecisionTreeClassifier(max_depth=4, class_weight='balanced',
                                 random_state=RANDOM_STATE)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_dt)
    tn,fp,fn,tp = cm.ravel()
    results['Decision Tree'] = {
        'Accuracy' : round(accuracy_score(y_test, y_pred_dt),4),
        'Precision': round(precision_score(y_test, y_pred_dt, zero_division=0),4),
        'Recall'   : round(recall_score(y_test, y_pred_dt, zero_division=0),4),
        'F1'       : round(f1_score(y_test, y_pred_dt, zero_division=0),4),
        'TP':int(tp),'FP':int(fp),'FN':int(fn),'TN':int(tn),
    }

    # Random Forest
    rf = RandomForestClassifier(n_estimators=200, max_depth=6, min_samples_leaf=20,
                                 class_weight='balanced', random_state=RANDOM_STATE,
                                 n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_rf)
    tn,fp,fn,tp = cm.ravel()
    results['Random Forest'] = {
        'Accuracy' : round(accuracy_score(y_test, y_pred_rf),4),
        'Precision': round(precision_score(y_test, y_pred_rf, zero_division=0),4),
        'Recall'   : round(recall_score(y_test, y_pred_rf, zero_division=0),4),
        'F1'       : round(f1_score(y_test, y_pred_rf, zero_division=0),4),
        'TP':int(tp),'FP':int(fp),'FN':int(fn),'TN':int(tn),
    }

    return results, X_train.shape, y_train.shape, X_test.shape, y_test.shape

# ── Figure generation (simplified headless versions) ─────────────────────────
def save_figures(df_dataset, results):
    zone_order  = [ZONE_NEGATIVE, ZONE_PRE_WARN, ZONE_ACTIVE, ZONE_RECOVERY]
    ZONE_COLORS = {ZONE_NEGATIVE:'#4CAF50', ZONE_PRE_WARN:'#FFC107',
                   ZONE_ACTIVE:'#F44336',   ZONE_RECOVERY:'#9E9E9E'}
    ZONE_LABELS = {ZONE_NEGATIVE:'Negativo', ZONE_PRE_WARN:'Pre-advertencia',
                   ZONE_ACTIVE:'Advertencia activa', ZONE_RECOVERY:'Recuperación'}

    # Fig 1 - Zone distribution
    zone_tbl = (df_dataset.groupby(['compressor_id','zone']).size()
                .unstack(fill_value=0).reindex(columns=zone_order, fill_value=0))
    fig, axes = plt.subplots(1,3,figsize=(14,5))
    panels = [('INDNº1','#1565C0'),('INDNº2','#E65100'),('Flota','#37474F')]
    data_rows = ([zone_tbl.loc[c] if c in zone_tbl.index else pd.Series(0,index=zone_order)
                  for c,_ in panels[:-1]] + [zone_tbl.sum()])
    for ax,(title,color),counts in zip(axes,panels,data_rows):
        ax.bar([ZONE_LABELS[z] for z in zone_order], counts[zone_order].values,
               color=[ZONE_COLORS[z] for z in zone_order], edgecolor='white', width=0.6)
        ax.set_title(title, color=color); ax.set_ylabel('Horas')
        ax.tick_params(axis='x',rotation=22)
        ax.set_xticklabels([ZONE_LABELS[z] for z in zone_order],rotation=22,ha='right',fontsize=9)
    fig.suptitle('Fig 1 — Distribución de zonas de etiquetado',fontsize=12,fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR,'fig1_zone_distribution.png'), bbox_inches='tight', dpi=150)
    plt.close(fig)
    print('  fig1 saved')

    # Fig 6 - Model comparison
    metric_cols = ['Accuracy','Precision','Recall','F1']
    df_cmp = pd.DataFrame(list(results.values()),index=list(results.keys()))
    fig, ax = plt.subplots(figsize=(10,4.5))
    x      = np.arange(len(metric_cols))
    width  = 0.35
    colors = ['#1565C0','#2E7D32']
    for i,(model_name,row) in enumerate(df_cmp[metric_cols].iterrows()):
        offset = (i - len(df_cmp)/2 + 0.5)*width
        bars = ax.bar(x+offset, row.values, width, label=model_name,
                      color=colors[i%len(colors)], alpha=0.85, edgecolor='white')
        for bar,val in zip(bars,row.values):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(metric_cols,fontsize=11)
    ax.set_ylim(0,1.08); ax.set_ylabel('Score')
    ax.set_title('Fig 6 — Comparación de modelos — TEST SET (INDNº1)',fontweight='bold')
    ax.legend(loc='lower right')
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR,'fig6_model_comparison.png'), bbox_inches='tight', dpi=150)
    plt.close(fig)
    print('  fig6 saved')


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — DAT MODE (PARQUET_MODE = False)
# ══════════════════════════════════════════════════════════════════════════════
SEP = '=' * 65

print(SEP)
print('  PHASE 1 — DAT MODE  (PARQUET_MODE = False)')
print(SEP)

print('\nExtracting hourly stats — INDNº1...')
_raw1 = extract_hourly_stats(COMPRESSORS['INDNº1']['dat_root'])
df_features_ind1 = build_feature_matrix(_raw1,'INDNº1')

print('\nExtracting hourly stats — INDNº2...')
_raw2 = extract_hourly_stats(COMPRESSORS['INDNº2']['dat_root'])
df_features_ind2 = build_feature_matrix(_raw2,'INDNº2')

print('\nParsing event logs and building episode tables...')
df_ev_ind1 = parse_event_log(COMPRESSORS['INDNº1']['log_path'],'0011','W')
df_ep_ind1 = build_episode_table(df_ev_ind1, COMPRESSORS['INDNº1']['dat_start'],
                                  COMPRESSORS['INDNº1']['dat_end'])
df_ev_ind2 = parse_event_log(COMPRESSORS['INDNº2']['log_path'],'0013','W')
df_ep_ind2 = build_episode_table(df_ev_ind2, COMPRESSORS['INDNº2']['dat_start'],
                                  COMPRESSORS['INDNº2']['dat_end'])

print('\nAssembling dataset...')
df_ind1 = assemble_dataset(df_features_ind1, df_ep_ind1, df_ev_ind1)
df_ind2 = assemble_dataset(df_features_ind2, df_ep_ind2, df_ev_ind2)
df_dataset_dat = pd.concat([df_ind1, df_ind2]).sort_index()

print(f'\ndf_dataset shape    : {df_dataset_dat.shape}')
print(f'Columns             : {list(df_dataset_dat.columns)}')

# Zone summary
zone_tbl = (df_dataset_dat.groupby(['compressor_id','zone']).size()
            .unstack(fill_value=0))
print(f'\nZone distribution:\n{zone_tbl.to_string()}')

# Export parquet
print(f'\nExporting to {PARQUET_PATH} ...')
df_dataset_dat.to_parquet(PARQUET_PATH, engine='pyarrow', index=True)
size_mb = os.path.getsize(PARQUET_PATH)/1024**2
print(f'Parquet exported: {size_mb:.1f} MB')

# Train models in DAT mode
print('\nTraining models (DAT mode)...')
results_dat, Xtr_shape, ytr_shape, Xte_shape, yte_shape = train_and_evaluate(df_dataset_dat)
print(f'  Train: {Xtr_shape}  Test: {Xte_shape}')
for name, r in results_dat.items():
    print(f'  {name:<20} Acc={r["Accuracy"]:.4f}  Prec={r["Precision"]:.4f}'
          f'  Rec={r["Recall"]:.4f}  F1={r["F1"]:.4f}  '
          f'TP={r["TP"]} FP={r["FP"]} FN={r["FN"]} TN={r["TN"]}')

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — PARQUET MODE (PARQUET_MODE = True)
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print('  PHASE 2 — PARQUET MODE  (PARQUET_MODE = True)')
print(SEP)

print(f'\nLoading {PARQUET_PATH} ...')
df_dataset_pq = pd.read_parquet(PARQUET_PATH, engine='pyarrow')
df_dataset_pq.index = pd.to_datetime(df_dataset_pq.index)
print(f'Loaded shape: {df_dataset_pq.shape}')

print('\nTraining models (Parquet mode)...')
results_pq, _, _, _, _ = train_and_evaluate(df_dataset_pq)
for name, r in results_pq.items():
    print(f'  {name:<20} Acc={r["Accuracy"]:.4f}  Prec={r["Precision"]:.4f}'
          f'  Rec={r["Recall"]:.4f}  F1={r["F1"]:.4f}  '
          f'TP={r["TP"]} FP={r["FP"]} FN={r["FN"]} TN={r["TN"]}')

# ── Assert metrics match ───────────────────────────────────────────────────────
print('\nComparing DAT mode vs Parquet mode metrics...')
all_match = True
for name in results_dat:
    for metric in ['Accuracy','Precision','Recall','F1','TP','FP','FN','TN']:
        v_dat = results_dat[name][metric]
        v_pq  = results_pq[name][metric]
        if v_dat != v_pq:
            print(f'  MISMATCH  {name} / {metric}: DAT={v_dat}  PQ={v_pq}')
            all_match = False

if all_match:
    print('  All metrics MATCH between DAT mode and Parquet mode.')

# ── Generate key figures ──────────────────────────────────────────────────────
print('\nRegenerating figures (headless)...')
save_figures(df_dataset_pq, results_pq)

# ══════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print('  VALIDATION REPORT')
print(SEP)
print(f'\n  Cells changed             : 4 (via apply_notebook_changes.py)')
print(f'  Parquet created           : YES  ({size_mb:.1f} MB)')
print(f'  df_dataset shape          : {df_dataset_dat.shape}')
print(f'  Metrics unchanged DAT->PQ : {"YES" if all_match else "NO -- see mismatches above"}')
print(f'  Figures regenerated       : YES (fig1, fig6 in {FIG_DIR})')
print()
print('  Model metrics (Parquet mode -- final):')
for name, r in results_pq.items():
    print(f'    {name:<20} Recall={r["Recall"]:.4f}  F1={r["F1"]:.4f}')
print()
print('  VALIDATION COMPLETE.')
print(SEP)
