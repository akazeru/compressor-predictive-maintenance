# PROJECT HANDOFF

## Objective
Predict oil/air filter differential-pressure warnings on KAESER CSDX165 rotary-screw compressors **24 hours before activation**, using 1-Hz DAT sensor data from the onboard SIGMA CONTROL 2 recorder.

---

## Dataset Sources

| Source | Format | Location (relative to `equipos\`) |
|---|---|---|
| DAT sensor files | Binary, 954,664 bytes/file, 1 file/hour | `Compresor CSDX165 Aire Industrial NºX\CSDX165_INDNºX\datarecorder\` |
| Event logs | UTF-8 text | `...\BF_*\reports_lang\CompressorMsgs.txt` |

**Active BF folders:**
- INDNº1: `BF_101803.1_1171_2026-05-27T09.48.42-04.00`
- INDNº2: `BF_101803.2_1001_2026-05-27T09.54.00-04.00`

---

## Compressors

| ID | Filter | DAT window | Episodes in-DAT | ML role |
|---|---|---|---|---|
| INDNº1 | Oil (0011 W) | 2026-03-18 → 2026-05-27 | 2 (E10: 1 onset · E11: 16 onsets) | **Test** |
| INDNº2 | Air (0013 W) | 2025-06-23 → 2026-05-27 | 4 (E6–E9, 3–6 onsets each) | **Train** |
| EMBNº1/EMBNº2 | — | — | 0 — gap 349–391 days | Excluded |

---

## Target Events
- `0011 W` — Oil Filter ΔP ↑ (binary pressure switch, not a continuous sensor)
- `0013 W` — Air Filter ΔP ↑ (same mechanism)
- Both treated as a unified `filter_dp_warning` class

---

## DAT Binary Structure
- **Header:** 4,264 bytes · **Record:** 264 bytes · **Count:** 3,600 records/file (1 Hz)
- **Per record:** `uint32 LE timestamp` + `130 × int16 LE channels`
- **Sentinel:** `−32768` (0x8000) → NaN
- **Key channels used:**

| ch | Name | Scale | Unit |
|---|---|---|---|
| 0 | Compressor status | — | bitmask |
| 4 | System pressure | ×0.01 | bar |
| 6 | Oil separator temperature | ×0.01 | °C |
| 9 | Inlet temperature | ×0.1 | °C |
| 12 | Compressor speed SP | ×10 | RPM |

**Not available:** ADT temperature (ch2, sensor not installed), motor current (ch15), torque (ch16).

---

## Final Dataset
- **Shape:** 9,745 rows × 12 columns
- **Unit:** 1 hour = 1 row (one DAT file)
- **Train:** INDNº2, 8,054 rows · **Test:** INDNº1, 1,667 rows
- **Class weights:** `{0: 0.571, 1: 4.003}` (balanced)

---

## Feature List (8 MVP features)

| Feature | Description |
|---|---|
| `p_mean_1h` | Mean discharge pressure (bar) |
| `p_std_1h` | Std dev discharge pressure |
| `oil_temp_mean_1h` | Mean oil separator temperature (°C) |
| `oil_temp_max_1h` | Max oil separator temperature |
| `speed_mean_1h` | Mean VFD speed setpoint (RPM) |
| `speed_std_1h` | Std dev speed setpoint |
| `load_frac_1h` | Fraction of hour compressor was loaded |
| `hours_loaded_since_clear` | Loaded hours accumulated since last filter clearance ← **dominant feature** |

---

## Label Strategy

| Zone | Definition | `label_extended` |
|---|---|---|
| `pre_warning` | [first_onset − 24 h, first_onset) ∩ negative | 1 |
| `active_warning` | [first_onset, last_clear] | 1 |
| `recovery` | (last_clear, last_clear + 4 h] | NaN (excluded) |
| `negative` | all other hours | 0 |

- **Positive class (train):** 1,006 rows · **Negative:** 7,048
- **Episode gap threshold:** 7 days (onsets within 7 days = same episode)
- **UTC/local offset:** max ±4 h — acceptable (episodes span days)

---

## Train / Test Strategy
- **Split:** cross-machine temporal — train on INDNº2 (air filter), test on INDNº1 (oil filter)
- **No random split** — temporal integrity enforced
- **Recovery rows** excluded from both splits

---

## Model Configurations

| Model | Key parameters |
|---|---|
| `DecisionTreeClassifier` | `max_depth=4, class_weight='balanced', random_state=42` |
| `RandomForestClassifier` | `n_estimators=200, max_depth=6, min_samples_leaf=20, class_weight='balanced', random_state=42, n_jobs=-1` |
| Keras MLP | `Dense(32,relu)→Dense(16,relu)→Dense(1,sigmoid)`, `Adam(lr=1e-3)`, `binary_crossentropy`, `EarlyStopping(patience=10)`, `StandardScaler` on train only |

---

## Final Metrics — TEST SET (INDNº1, cross-machine)

| Model | Accuracy | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|
| Decision Tree | 0.7061 | 0.4535 | **0.8537** | **0.5923** | 356 | 429 | 61 | 821 |
| Random Forest | 0.6977 | 0.4458 | **0.8585** | 0.5869 | 358 | 445 | 59 | 805 |
| MLP | requires TF in Jupyter | — | — | — | — | — | — | — |

**Primary metric:** Recall. **Root split (DT):** `hours_loaded_since_clear`. **Top-3 RF:** `hours_loaded_since_clear`, `speed_mean_1h`, `oil_temp_mean_1h`.

---

## Figures Generated (`figures/`, PNG 150 dpi)

| File | Content |
|---|---|
| `fig1_zone_distribution.png` | Zone counts per compressor + fleet total |
| `fig2_episode_timeline.png` | Calendar timeline with colored zone bands |
| `fig3_decision_tree.png` | Full depth-4 tree (`plot_tree`) |
| `fig4_feature_importance.png` | DT vs RF feature importance, side-by-side |
| `fig5_confusion_matrices.png` | Confusion matrices with Recall/Specificity annotations |
| `fig6_model_comparison.png` | Grouped bar chart + printed metrics table |

---

## Repository Structure

```
compressor-predictive-maintenance/
├── notebooks/
│   └── proyecto_ia.ipynb        ← 36 cells, Commits 1–4
├── docs/
│   ├── report_outline.md        ← 12-section report scaffold
│   ├── presentation_outline.md  ← 14-slide guide with speaking points
│   └── responsibility_matrix.md ← 4-role assignment + checklists
├── src/                         ← empty
└── README.md

proyecto/ (root)
├── equipos/                     ← raw DAT + event logs (4 compressors)
├── figures/                     ← fig1–fig6
├── reference/                   ← KAESER manual PDF
├── dat_parser.py                ← standalone DAT parser module
└── _verify_commit2/3/4.py       ← end-to-end verification scripts
```

---

## Known Limitations

1. **6 total labeled episodes** — high metric variance (±15 pp F1 per episode)
2. **INDNº1 test has 25% positive rate** vs 13% in train — test set skewed toward warning condition
3. **No continuous ΔP sensor** — all features are indirect proxies
4. **ADT, current, torque channels absent** — incomplete load signal
5. **ch7 scale unresolved** — used as rank-order feature only
6. **MLP not verified headless** — TensorFlow not in sandbox; runs in Jupyter
7. **2-compressor dataset** — no fleet-wide generalization test

---

## Open Tasks

- [ ] Run full notebook in Jupyter (kernel restart → run all) to confirm MLP cell executes
- [ ] Write report using `docs/report_outline.md` as scaffold
- [ ] Build PowerPoint using `docs/presentation_outline.md`
- [ ] (Future) LOEO-CV for metric variance estimation
- [ ] (Future) Threshold optimization (precision ≥ 0.6 constraint)
- [ ] (Future) Extend to EMBNº1/EMBNº2 when new episodes accumulate

---

# CURRENT STATUS

**Notebook:** 36 cells, all four commits complete and verified end-to-end.  
**Figures:** 6 PNG files saved to `figures/`.  
**Documentation:** 3 Markdown scaffolds in `docs/`.  
**Pending:** report writing, PPT assembly, Jupyter full run with TensorFlow.

---

# NEXT ACTION

**Open `notebooks/proyecto_ia.ipynb` in Jupyter, run all cells, confirm MLP cell output, then begin report writing starting with §4 (Data Sources) and §5 (Data Engineering) using `docs/report_outline.md`.**