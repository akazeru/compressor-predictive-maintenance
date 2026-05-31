# Datos del Proyecto

Este directorio contiene el paquete mínimo de reproducibilidad del notebook.  
Los archivos DAT originales (~9.3 GB) **no** están incluidos en el repositorio.

---

## Contenido

```
data/
├── processed/
│   └── df_dataset.parquet        ← dataset final (~3 MB) — suficiente para correr los modelos
├── events/
│   ├── CompressorMsgs_INDNº1.txt ← historial de eventos INDNº1 (filtro aceite, 0011 W)
│   └── CompressorMsgs_INDNº2.txt ← historial de eventos INDNº2 (filtro aire, 0013 W)
└── README.md                     ← este archivo
```

---

## df_dataset.parquet

### Qué contiene

El dataset final ensamblado a partir de los archivos DAT de los dos compresores activos.
Una fila representa una hora completa de operación de un compresor.

| Columna | Tipo | Descripción |
|---|---|---|
| `hour_utc` | DatetimeIndex | Marca temporal UTC del inicio de la hora (índice) |
| `compressor_id` | str | `'INDNº1'` o `'INDNº2'` |
| `p_mean_1h` | float | Presión de descarga media (bar) |
| `p_std_1h` | float | Desviación estándar de presión (bar) |
| `oil_temp_mean_1h` | float | Temperatura separador media (°C) |
| `oil_temp_max_1h` | float | Temperatura separador máxima (°C) |
| `speed_mean_1h` | float | Velocidad VFD media (RPM) |
| `speed_std_1h` | float | Desviación estándar velocidad (RPM) |
| `load_frac_1h` | float | Fracción del tiempo en estado cargado [0, 1] |
| `hours_loaded_since_clear` | float | Horas acumuladas desde el último despeje del filtro |
| `zone` | str | `'negative'`, `'pre_warning'`, `'active_warning'`, `'recovery'` |
| `label_strict` | float | 1.0 (pre_warning) / 0.0 (negative) / NaN (otros) |
| `label_extended` | float | 1.0 (pre+active) / 0.0 (negative) / NaN (recovery) |

### Estadísticas

| Split | Compressor | Filas totales | Filas sin recovery | Positivos | Negativos |
|---|---|---|---|---|---|
| Train | INDNº2 | 8.070 | 8.054 | 1.006 | 7.048 |
| Test | INDNº1 | 1.675 | 1.667 | 417 | 1.250 |
| **Total** | ambos | **9.745** | **9.721** | **1.423** | **8.298** |

### Cómo cargarlo

```python
import pandas as pd

df_dataset = pd.read_parquet('data/processed/df_dataset.parquet')

# Separar por compresor
df_ind1 = df_dataset[df_dataset['compressor_id'] == 'INDNº1']
df_ind2 = df_dataset[df_dataset['compressor_id'] == 'INDNº2']

# Features y target para los modelos
FEAT_COLS = [
    'p_mean_1h', 'p_std_1h', 'oil_temp_mean_1h', 'oil_temp_max_1h',
    'speed_mean_1h', 'speed_std_1h', 'load_frac_1h', 'hours_loaded_since_clear',
]
TARGET_COL = 'label_extended'
ZONE_RECOVERY = 'recovery'

df_usable = df_dataset[df_dataset['zone'] != ZONE_RECOVERY].copy()
df_train  = df_usable[df_usable['compressor_id'] == 'INDNº2']
df_test   = df_usable[df_usable['compressor_id'] == 'INDNº1']

X_train = df_train[FEAT_COLS].values
y_train = df_train[TARGET_COL].values.astype(int)
X_test  = df_test[FEAT_COLS].values
y_test  = df_test[TARGET_COL].values.astype(int)
```

### Cómo fue generado

El parquet es la salida del pipeline del notebook `notebooks/proyecto_ia.ipynb` (celdas 1–21).
Para regenerarlo desde los archivos DAT originales:
1. Configurar `PARQUET_MODE = False` y `ROOT = <ruta a equipos/>` en la celda de configuración.
2. Ejecutar todas las celdas del notebook.
3. Ejecutar la celda de exportación (al final de la sección de Dataset).

---

## Archivos de eventos

Los archivos `CompressorMsgs_*.txt` son extraídos directamente de las carpetas BF
del controlador SIGMA CONTROL 2 mediante el software BF de KAESER.

Son necesarios para regenerar las tablas de episodios usadas en la Figura 2 y para
el cálculo de `hours_loaded_since_clear` si se parte desde cero.

### Formato

Una línea por evento:
```
<código>  <tipo>  <estado>  <timestamp ISO8601 con zona horaria>
```

Ejemplo:
```
0013  W  c  2025-08-14T06:23:11-04:00
0013  W  g  2025-08-14T14:37:02-04:00
```

Donde:
- `c` = onset (advertencia activada)
- `g` = clearance (advertencia despejada por el operador)

---

## Archivos DAT — instrucciones para ejecución completa (Opción B)

Si deseas regenerar el dataset desde los archivos DAT originales:

### Estructura de directorios requerida

```
equipos/                                          ← ROOT en la celda de config
├── Compresor CSDX165 Aire Industrial Nº1/
│   └── CSDX165_INDNº1/
│       ├── BF_101803.1_1171_2026-05-27T09.48.42-04.00/
│       │   └── reports_lang/
│       │       └── CompressorMsgs.txt
│       └── datarecorder/
│           ├── 2026/03/18/mcs_00.dat ... mcs_23.dat
│           └── ...
└── Compresor CSDX165 Aire Industrial Nº2/
    └── CSDX165_INDNº2/
        ├── BF_101803.2_1001_2026-05-27T09.54.00-04.00/
        │   └── reports_lang/
        │       └── CompressorMsgs.txt
        └── datarecorder/
            ├── 2025/06/23/mcs_00.dat ... mcs_23.dat
            └── ...
```

### Especificación del archivo DAT

| Campo | Valor |
|---|---|
| Tamaño por archivo | 954.664 bytes exactos |
| Registros | 3.600 por archivo (1 Hz × 3.600 s = 1 hora) |
| Bytes por registro | 264 (4 bytes timestamp uint32 LE + 130 × int16 LE) |
| Valor centinela | -32.768 (0x8000) → NaN |
| Número de compresores | INDNº1: ~1.675 archivos / INDNº2: ~8.070 archivos |
| Tamaño total | ~9,3 GB |

---

## Google Colab — instrucciones

### Preparación (una sola vez)

1. Subir a Google Drive:
   - `data/processed/df_dataset.parquet`
   - `data/events/CompressorMsgs_INDNº1.txt`
   - `data/events/CompressorMsgs_INDNº2.txt`
   - `notebooks/proyecto_ia.ipynb`

2. Crear la carpeta `figures/` en Drive (el notebook la crea automáticamente si no existe).

### Al abrir el notebook en Colab

```python
# Celda 1 — montar Drive (ejecutar primero)
from google.colab import drive
drive.mount('/content/drive')

# Celda 2 — instalar pyarrow (las demás dependencias ya están en Colab)
!pip install -q pyarrow

# Celda 3 — en la celda de configuración del notebook, cambiar:
# IN_COLAB detectado automáticamente
# PROJ_ROOT = '/content/drive/MyDrive/compressor-project'  ← ajustar al nombre de tu carpeta
# PARQUET_MODE = True  ← mantener True
```

### Tiempos estimados en Colab (CPU runtime)

| Sección | Tiempo |
|---|---|
| Instalación pyarrow | ~20 s |
| Montaje Drive | ~10 s |
| Carga parquet | < 2 s |
| Entrenamiento DT + RF | < 30 s |
| Entrenamiento MLP (TF instalado) | ~60–120 s |
| Generación de 6 figuras | ~30 s |
| **Total** | **~4 minutos** |
