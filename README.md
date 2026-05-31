# Mantenimiento Predictivo — Compresores KAESER CSDX165

**Proyecto Final · Curso IA Aplicada a la Industria · USACH, Semestre 1, 2026**  
**Autor:** Felipe Soto

---

## Descripción

Sistema de predicción de advertencias de diferencial de presión en filtros de compresores rotativos de tornillo KAESER CSDX165, con un horizonte de anticipación de **24 horas**, a partir de datos sensoriales del controlador SIGMA CONTROL 2.

| Evento objetivo | Tipo de filtro | Compressor |
|---|---|---|
| `0011 W` — Oil Filter ΔP ↑ | Aceite | INDNº1 (test) |
| `0013 W` — Air Filter ΔP ↑ | Aire | INDNº2 (train) |

**Resultado principal:** Recall ≈ 85 % en evaluación cross-machine (modelo entrenado en INDNº2, evaluado en INDNº1).

---

## Inicio rápido — 3 pasos

### Opción A — Con dataset preprocesado (recomendado para colaboradores)

No requiere los archivos DAT de 9.3 GB. Ejecuta los modelos directamente desde el dataset ya procesado.

```bash
# 1. Clonar el repositorio
git clone https://github.com/akazeru/compressor-predictive-maintenance.git
cd compressor-predictive-maintenance

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Abrir el notebook
jupyter notebook notebooks/proyecto_ia.ipynb
```

En el notebook, asegurarse de que la celda de configuración tenga:
```python
PARQUET_MODE = True   # ← valor por defecto
```

Luego: **Kernel → Restart & Run All**. Las celdas de parseo DAT se omiten automáticamente y los modelos cargan desde `data/processed/df_dataset.parquet`.

---

### Opción B — Con archivos DAT completos (reproducibilidad total)

Requiere acceso a los archivos DAT originales (~9.3 GB). Contactar al autor para obtenerlos.

```bash
# 1-2. Igual que Opción A

# 3. Copiar los archivos DAT al directorio esperado:
#    equipos/
#      Compresor CSDX165 Aire Industrial Nº1/CSDX165_INDNº1/datarecorder/
#      Compresor CSDX165 Aire Industrial Nº2/CSDX165_INDNº2/datarecorder/
#    Ver data/README.md para la estructura completa.

# 4. Abrir el notebook y cambiar:
#    PARQUET_MODE = False
#    ROOT = r'ruta\a\equipos'   # ajustar a tu máquina

# 5. Kernel → Restart & Run All
#    Tiempo estimado de procesamiento DAT: ~80 segundos
```

---

### Opción C — Google Colab

```python
# Celda 1: Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Celda 2: Instalar dependencia adicional
!pip install -q pyarrow

# Celda 3: Clonar o subir el repositorio a Drive y ajustar:
#   PROJ_ROOT = '/content/drive/MyDrive/compressor-predictive-maintenance'
#   PARQUET_MODE = True
```

Ver sección completa de instrucciones Colab en `data/README.md`.

---

## Estructura del repositorio

```
compressor-predictive-maintenance/
│
├── notebooks/
│   └── proyecto_ia.ipynb         ← notebook principal (36 celdas)
│
├── src/
│   └── dat_parser.py             ← módulo de referencia del parser DAT
│
├── data/
│   ├── processed/
│   │   └── df_dataset.parquet    ← dataset final (9.745 filas × 12 columnas)
│   ├── events/
│   │   ├── CompressorMsgs_INDNº1.txt   ← log de eventos filtro aceite
│   │   └── CompressorMsgs_INDNº2.txt   ← log de eventos filtro aire
│   └── README.md                 ← instrucciones de datos
│
├── figures/                      ← figuras exportadas (PNG 150 dpi)
│   ├── fig1_zone_distribution.png
│   ├── fig2_episode_timeline.png
│   ├── fig3_decision_tree.png
│   ├── fig4_feature_importance.png
│   ├── fig5_confusion_matrices.png
│   └── fig6_model_comparison.png
│
├── docs/
│   ├── report_outline.md
│   ├── presentation_outline.md
│   └── responsibility_matrix.md
│
├── requirements.txt
├── .gitignore
└── README.md                     ← este archivo
```

---

## Dataset

| Parámetro | Valor |
|---|---|
| Filas | 9.745 (1 fila = 1 hora de operación) |
| Features | 8 (MVP) |
| Target | `label_extended` ∈ {0, 1, NaN} |
| Train | INDNº2 — 8.054 filas (sin recovery) |
| Test | INDNº1 — 1.667 filas (sin recovery) |
| Positivos train | 1.006 (12.5 %) |
| Positivos test | 417 (25.0 %) |

**Features del modelo:**

| Feature | Descripción |
|---|---|
| `p_mean_1h` | Presión de descarga media (bar) |
| `p_std_1h` | Desviación estándar de presión |
| `oil_temp_mean_1h` | Temperatura separador aceite media (°C) |
| `oil_temp_max_1h` | Temperatura separador aceite máxima |
| `speed_mean_1h` | Velocidad VFD media (RPM) |
| `speed_std_1h` | Desviación estándar velocidad VFD |
| `load_frac_1h` | Fracción del tiempo en estado cargado |
| `hours_loaded_since_clear` | Horas acumuladas desde último cambio de filtro |

---

## Resultados

| Modelo | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Decision Tree (depth=4) | 0.7061 | 0.4535 | **0.8537** | **0.5923** |
| Random Forest (n=200, d=6) | 0.6977 | 0.4458 | **0.8585** | 0.5869 |

Evaluación cross-machine: entrenado en INDNº2 (filtro de aire), evaluado en INDNº1 (filtro de aceite).  
**Métrica primaria: Recall** — coste de FN (advertencia perdida) > coste de FP (falsa alarma).

---

## Dependencias

```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
scikit-learn>=1.0.0
pyarrow>=8.0.0
tensorflow>=2.9.0    # opcional — solo para la celda MLP
```

Instalar: `pip install -r requirements.txt`

---

## Datos de contacto

**Autor:** Felipe Soto · fsoto532@gmail.com  
**Repositorio:** https://github.com/akazeru/compressor-predictive-maintenance
