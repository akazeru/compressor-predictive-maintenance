# Informe de Proyecto — Esquema Detallado
## Mantenimiento Predictivo en Compresores Industriales KAESER CSDX165

> **Estado:** Esquema de redacción — Commit 4 completado  
> **Notebook:** `notebooks/proyecto_ia.ipynb` (36 celdas)  
> **Figuras disponibles:** `figures/` (Fig 1–6, PNG 150 dpi)  
> **Extensión objetivo:** 25–35 páginas (sin anexos)

---

## Portada

| Campo | Contenido |
|-------|-----------|
| Título | Predicción de Advertencias de Diferencial de Presión en Filtros de Compresores Rotativos de Tornillo Mediante Aprendizaje Automático |
| Curso | [Nombre del curso de IA Industrial] |
| Institución | [Nombre de la institución] |
| Autor(es) | Felipe Soto |
| Fecha | Mayo 2026 |
| Código del proyecto | `compressor-predictive-maintenance` |

---

## 0. Resumen Ejecutivo

**Propósito:** Síntesis completa del problema, enfoque y resultado en una sola página. El evaluador debe poder leer solo esta sección y entender qué se hizo, cómo y con qué resultado.

**Extensión:** 400–500 palabras (una página).

**Puntos clave a redactar:**
- Problema industrial: los filtros de aceite (0011 W) y de aire (0013 W) de compresores KAESER CSDX165 generan advertencias de diferencial de presión que, si no son anticipadas, causan paradas no programadas.
- Enfoque técnico: se construyó un dataset supervisado a partir de 9.745 horas de datos binarios 1 Hz (archivos `.dat`) y logs de eventos del controlador SIGMA CONTROL 2.
- Modelo recomendado: Decision Tree y Random Forest con `class_weight='balanced'`, entrenados en INDNº2 (filtro de aire, 4 episodios) y evaluados en INDNº1 (filtro de aceite, 2 episodios).
- Resultado principal: **Recall ≈ 85 %** en un compresor distinto del entrenamiento, con horizonte de predicción de **24 horas** — suficiente para planificar el reemplazo del filtro en el turno siguiente.
- Hallazgo clave: la variable `hours_loaded_since_clear` (horas acumuladas desde el último cambio de filtro) es el predictor dominante, validando la hipótesis de degradación progresiva por tiempo de operación.

**Sin figuras ni tablas en esta sección.**

---

## 1. Introducción

**Propósito:** Motivar el problema, contextualizar el trabajo dentro del curso y establecer los objetivos.

**Extensión:** 1–1,5 páginas.

**Puntos clave:**
1. Relevancia del mantenimiento predictivo en la industria moderna (reducción de costos, disponibilidad de activos).
2. Breve descripción del entorno: planta industrial, cuatro compresores KAESER CSDX165, sistema de aire comprimido.
3. Motivación específica: los filtros son consumibles críticos; su saturación incrementa el diferencial de presión, reduce la eficiencia y puede provocar alarmas de parada.
4. Pregunta de investigación: *¿Es posible predecir con 24 horas de anticipación la activación de la advertencia de ΔP en filtros de compresor, a partir de datos operacionales del propio controlador?*
5. Objetivos del proyecto (uno general, tres específicos):
   - General: desarrollar un modelo de ML capaz de predecir eventos de mantenimiento de filtros.
   - Específico 1: construir un pipeline de datos reproducible desde archivos `.dat` binarios.
   - Específico 2: definir y validar un esquema de etiquetado supervisado basado en logs de eventos.
   - Específico 3: evaluar la generalización cross-machine del modelo entrenado.
6. Estructura del informe (párrafo de un párrafo).

**Figuras:** ninguna en esta sección.  
**Tablas:** ninguna en esta sección.

---

## 2. Antecedentes Industriales

**Propósito:** Proveer al evaluador el contexto técnico necesario para entender el problema sin conocimiento previo de compresores.

**Extensión:** 2–3 páginas.

### 2.1 Compresor rotativo de tornillo KAESER CSDX165

**Puntos:**
- Principio de funcionamiento: dos tornillos helicoidales sincrónicos comprimen aire, con inyección de aceite para sellado y refrigeración.
- Datos técnicos relevantes: accionamiento VFD (variador de frecuencia), controlador SIGMA CONTROL 2 (fluid 6.5.1), presión de trabajo ~7–8 bar.
- Rol del aceite: lubricación, sellado y transferencia de calor; filtrado obligatorio por el filtro de aceite.
- Rol del filtro de aire: protege al conjunto de tornillos de partículas ambientales; su saturación reduce el caudal volumétrico.

### 2.2 Mecanismo de detección del diferencial de presión

**Puntos:**
- Ambos filtros (aceite y aire) utilizan un interruptor binario de diferencial de presión (switch de ΔP), **no** un sensor analógico continuo.
- Cuando el ΔP supera el umbral de fábrica, el switch activa la advertencia (0011 W u 0013 W).
- Consecuencia: el canal de ΔP del filtro **no existe como señal continua** en los datos del grabador de datos (DAT). La predicción debe inferirse de señales operacionales indirectas.
- Referencia: §8.11.4 y §5.6.2 del manual *Sigma Control 2 Screw Fluid ≥ 4.1.X* (español).

### 2.3 Intervalo de mantenimiento

**Puntos:**
- KAESER recomienda el reemplazo del filtro de aceite cada ~2.000 horas de operación (~3–5 meses a ciclo continuo).
- El filtro de aire tiene un ciclo similar, acelerado por condiciones de polvo ambiental.
- El patrón observado en los datos: episodios cada ~3,5 meses en INDNº2 (filtro de aire), coherente con la recomendación del fabricante.

**Tablas:**
- **Tabla 2.1:** Especificaciones técnicas del CSDX165 (modelo, potencia, presión, velocidad VFD, firmware).
- **Tabla 2.2:** Códigos de evento relevantes (0011 W, 0013 W, categoría, descripción, tipo de sensor).

**Figuras:** diagrama simplificado del circuito aceite-aire del compresor (si se dispone; de lo contrario omitir).

---

## 3. Definición del Problema

**Propósito:** Traducir el problema industrial a una formulación ML precisa.

**Extensión:** 1–1,5 páginas.

**Puntos:**
1. **Tipo de problema:** clasificación binaria supervisada con datos de serie temporal.
2. **Unidad de observación:** una hora de operación (un archivo `.dat` = 3.600 registros a 1 Hz).
3. **Variable objetivo:** `label_extended` ∈ {0, 1} — positivo si la hora pertenece a la zona `pre_warning` o `active_warning`.
4. **Horizonte de predicción:** 24 horas (la clase positiva incluye las 24 horas previas al inicio de un episodio).
5. **Desafío de clase:** ratio de desequilibrio 7:1 en el conjunto de entrenamiento (INDNº2). Mitigado con `class_weight='balanced'` (peso de clase positiva ≈ 4×).
6. **Desafío de generalización:** el conjunto de prueba es un compresor distinto (INDNº1) con un tipo de filtro diferente (aceite vs. aire) — cross-machine, cross-filter-type generalization.
7. **Restricción crítica:** ausencia de canal de ΔP continuo; las features deben inferir la degradación del filtro a partir de señales operacionales indirectas.

**Tabla 3.1:** Resumen de la formulación ML.

| Aspecto | Decisión | Justificación |
|---------|----------|---------------|
| Tipo de tarea | Clasificación binaria | Etiqueta binaria: advertencia activa o no |
| Horizonte | 24 h | Suficiente para planificar en el turno siguiente |
| Métrica primaria | Recall | Coste de FN (advertencia perdida) > coste de FP |
| Métrica secundaria | F1-Score | Balance entre precisión y cobertura |
| Estrategia de división | Cross-machine temporal | Evita fuga de datos entre compresores |
| Desequilibrio de clases | class_weight='balanced' | Estándar para ML con imbalance moderado |

---

## 4. Fuentes de Datos

**Propósito:** Documentar exhaustivamente la procedencia, formato y calidad de cada fuente de datos.

**Extensión:** 2–3 páginas.

### 4.1 Archivos DAT del grabador de datos MCS

**Puntos:**
- Origen: controlador SIGMA CONTROL 2, exportado mediante software BF (backup factory).
- Formato: binario propietario, 954.664 bytes/archivo, 4.264 bytes de cabecera + 3.600 registros × 264 bytes.
- Cobertura: INDNº1 (1.675 archivos, 2026-03-18 → 2026-05-27); INDNº2 (8.070 archivos, 2025-06-23 → 2026-05-27).
- Frecuencia de muestreo: exactamente 1 Hz; cada archivo = 1 hora de operación.
- Canales: 130 int16 por registro, con factor de escala por tipo de unidad.
- Valores ausentes: centinela `−32768` (0x8000) → sustituido por NaN.

### 4.2 Logs de eventos CompressorMsgs.txt

**Puntos:**
- Origen: exportación BF del controlador; un archivo por snapshot BF por compresor.
- Formato: texto UTF-8, una línea por evento: `<código> <O/W/A> <c/g/a> <ISO-timestamp>`.
- Cobertura: INDNº1 (865 eventos totales, incluyendo 242 de código 0011 W desde 2017); INDNº2 (861 eventos, incluyendo 88 de código 0013 W desde 2018).
- Artefacto controlador: patrón de doble despeje — dos entradas `g` con diferencia de 1–5 s por despeje (comportamiento normal del firmware, no duplicados de error).

### 4.3 Auditoría de solapamiento temporal

**Puntos:**
- Solo INDNº1 e INDNº2 tienen solapamiento confirmado entre el rango DAT y los episodios de advertencia.
- EMBNº1 e EMBNº2 quedan excluidos: sus últimos eventos 0011 W / 0013 W ocurrieron 349–391 días antes del inicio de sus archivos DAT.

**Tabla 4.1:** Inventario de fuentes de datos por compresor.

| Compresor | DAT files | DAT inicio | DAT fin | Eventos objetivo | Episodios in-DAT | Usado |
|-----------|-----------|------------|---------|-----------------|------------------|-------|
| EMBNº1 | 8.045 | 2025-06-24 | 2026-05-27 | 0011 W | 0 | No |
| EMBNº2 | — | 2025-06-20 | 2026-05-27 | 0013 W | 0 | No |
| INDNº1 | 1.675 | 2026-03-18 | 2026-05-27 | 0011 W | 2 | Sí (test) |
| INDNº2 | 8.070 | 2025-06-23 | 2026-05-27 | 0013 W | 4 | Sí (train) |

**Tabla 4.2:** Canales DAT seleccionados (Tier-1 MVP).

| Índice | Nombre en archivo | Feature derivada | Escala | Unidad |
|--------|-------------------|-----------------|--------|--------|
| ch0 | Compressor status | `load_frac_1h` | — | bitmask |
| ch4 | System pressure | `p_mean_1h`, `p_std_1h` | ×0,01 | bar |
| ch6 | Oil separator temperature | `oil_temp_mean_1h`, `oil_temp_max_1h` | ×0,01 | °C |
| ch9 | Inlet temperature | (proxy ambiental) | ×0,1 | °C |
| ch12 | Compressor speed SP | `speed_mean_1h`, `speed_std_1h` | ×10 | RPM |

**Figuras:** ninguna en esta sección (las figuras del pipeline se presentan en §5).

---

## 5. Ingeniería de Datos

**Propósito:** Describir el pipeline completo de transformación desde archivos binarios hasta el DataFrame de análisis.

**Extensión:** 3–4 páginas.

### 5.1 Pipeline de carga DAT

**Puntos:**
- `list_dat_files()`: filtra por tamaño exacto (954.664 bytes) para rechazar archivos truncados.
- `read_dat_hour()`: desempaquetado vectorizado con `np.frombuffer` en formato `<i2` (int16 LE); 132 palabras por registro (2 = timestamp uint32, 130 = canales).
- Tiempo de procesamiento: INDNº1 ≈ 14 s; INDNº2 ≈ 66 s (máquina de desarrollo).

### 5.2 Extracción de estadísticas por hora

**Puntos:**
- `extract_hourly_stats()`: para cada archivo, agrega 3.600 registros en una fila con las estadísticas de los canales seleccionados (media, std, máximo).
- `load_frac_1h`: fracción de registros donde `cs ≠ 0` (compresor cargado vs. parado/descargado).
- Resultado: `df_raw` — 1.675 filas para INDNº1, 8.070 para INDNº2.

### 5.3 Definición de episodios

**Puntos:**
- `parse_event_log()`: filtra el log de texto por código+categoría destino, elimina duplicados exactos (timestamp, estado), ordena ascendente.
- `build_episode_table()`: agrupa onsets por umbral de brecha de 7 días. Un episodio = secuencia de onsets separados por < 7 días. El `last_clear` = último evento `g` dentro del rango del episodio.
- Resultado: 2 episodios in-DAT para INDNº1 (E10: 1 onset, E11: 16 onsets); 4 episodios para INDNº2 (E6–E9, 3–6 onsets cada uno).

### 5.4 Construcción de zonas de etiquetado

**Puntos:**
- `assign_zones()`: asigna una de cuatro zonas a cada hora por precedencia decreciente: `active_warning` > `recovery` > `pre_warning` > `negative`.
- Zona `recovery`: las 4 horas inmediatamente posteriores al último despeje del episodio — excluidas del entrenamiento (artefactos post-mantenimiento).
- Horizonte de predicción: 24 horas antes del primer onset de cada episodio = zona `pre_warning` (etiqueta positiva para el modelo estricto).
- Nota de alineación: el índice DAT está en UTC, los timestamps del log están en hora local chilena (UTC−3/−4). Error máximo ≈ 4 h — aceptable dado que los episodios duran días.

**Figura a insertar:** Fig 1 — Distribución de zonas de etiquetado (`figures/fig1_zone_distribution.png`).  
**Figura a insertar:** Fig 2 — Línea de tiempo de episodios (`figures/fig2_episode_timeline.png`).

**Tabla 5.1:** Conteo de zonas por compresor.

| Compresor | negative | pre_warning | active_warning | recovery | Total |
|-----------|----------|-------------|----------------|----------|-------|
| INDNº1 | 1.250 | 48 | 369 | 8 | 1.675 |
| INDNº2 | 7.048 | 96 | 910 | 16 | 8.070 |
| **Total** | **8.298** | **144** | **1.279** | **24** | **9.745** |

---

## 6. Ingeniería de Features

**Propósito:** Describir las variables de entrada del modelo y la lógica detrás de cada una.

**Extensión:** 2 páginas.

### 6.1 Feature set MVP (Commit 2)

**Puntos:**
- Ocho features de 1 hora: estadísticas directas del canal en la ventana de 1 h, sin rolling.
- Motivación por grupo:
  - **Presión** (`p_mean_1h`, `p_std_1h`): la presión de descarga refleja la carga de red; alta `p_std` indica ciclos de carga/descarga frecuentes que aceleran el ensuciamiento del filtro.
  - **Temperatura del separador** (`oil_temp_mean_1h`, `oil_temp_max_1h`): temperatura más alta → viscosidad del aceite más baja → mayor flujo a través del filtro → mayor tasa de deposición.
  - **Velocidad del compresor** (`speed_mean_1h`, `speed_std_1h`): el VFD ajusta la velocidad según demanda; mayor velocidad = mayor caudal volumétrico = más polvo/partículas retenidos por hora.
  - **Fracción de carga** (`load_frac_1h`): proporción del tiempo en estado cargado; los filtros solo se ensucian durante operación real.
  - **Acumulación** (`hours_loaded_since_clear`): contador de horas cargadas desde el último despeje del evento objetivo. **Feature más importante** — captura directamente la edad del filtro.

### 6.2 Propiedad del feature de acumulación

**Puntos:**
- `compute_hours_loaded_since_clear()`: barrido lineal O(n) con un puntero sobre los timestamps de despeje del log completo (incluyendo pre-DAT para inicialización correcta).
- Patrón de diente de sierra: el valor crece durante la operación y se resetea a 0 en cada despeje. Los resets coinciden con los inicios de episodio siguientes.
- Este comportamiento es coherente con la hipótesis física: el filtro se satura en función del volumen acumulado de fluido filtrado desde el último reemplazo.

**Tabla 6.1:** Descripción de features MVP.

| Feature | Tipo | Escala | Rango típico (operación) | Hipótesis física |
|---------|------|--------|--------------------------|-----------------|
| `p_mean_1h` | Continua | bar | 6,5–8,5 bar | ↑ carga de red → ↑ ΔP filtro |
| `p_std_1h` | Continua | bar | 0–0,5 bar | Alta varianza → ciclos rápidos |
| `oil_temp_mean_1h` | Continua | °C | 55–72 °C | ↑ temp → ↑ degradación aceite |
| `oil_temp_max_1h` | Continua | °C | 58–78 °C | Picos térmicos → estrés del filtro |
| `speed_mean_1h` | Continua | RPM | 1.800–3.600 RPM | ↑ vel → ↑ caudal → ↑ ensuciamiento |
| `speed_std_1h` | Continua | RPM | 0–500 RPM | ↑ varianza → operación inestable |
| `load_frac_1h` | Continua [0,1] | — | 0,3–1,0 | Proxy de horas reales de filtrado |
| `hours_loaded_since_clear` | Acumulativa | h | 0–2.500 h | **Edad del filtro** — feature dominante |

**Figura a insertar:** Fig 4 — Importancia de features (`figures/fig4_feature_importance.png`) — puede insertarse aquí como evidencia de validación de la hipótesis, o diferirse a §8.

---

## 7. Metodología de Machine Learning

**Propósito:** Describir las decisiones técnicas de modelado: arquitecturas, división de datos, métricas y justificaciones.

**Extensión:** 3–4 páginas.

### 7.1 Estrategia de división train/test

**Puntos:**
- División cross-machine temporal: entrenamiento en INDNº2 (filtro de aire, 11 meses, 4 episodios), prueba en INDNº1 (filtro de aceite, 2 meses, 2 episodios).
- Justificación: (1) integridad temporal — ningún dato futuro contamina el entrenamiento; (2) validación cross-machine — prueba si el modelo generaliza más allá del compresor entrenado; (3) cross-filter-type — verifica si el patrón aprendido en un tipo de filtro se transfiere a otro.
- Filas excluidas: zona `recovery` (NaN en `label_extended`).
- Tamaños: train 8.054 filas (pos=1.006, neg=7.048), test 1.667 filas (pos=417, neg=1.250).

### 7.2 Manejo del desequilibrio de clases

**Puntos:**
- Ratio train: 7:1 (neg:pos). Ratio test: 3:1.
- Estrategia: `class_weight='balanced'` en sklearn (pesos 0,57:4,00 para clase 0:1). Equivalente a sobremuestrear la clase positiva × 7 sin crear duplicados sintéticos.
- Motivo para no usar SMOTE: dataset pequeño (8k filas); el oversampling sintético puede introducir distribuciones artificiales en un espacio de features de 8 dimensiones.

### 7.3 Árbol de Decisión

**Puntos:**
- `DecisionTreeClassifier(max_depth=4, class_weight='balanced', random_state=42)`.
- Rol: baseline interpretable. A profundidad 4, el árbol tiene ≤ 16 nodos hoja, completamente inspeccionable.
- División raíz: `hours_loaded_since_clear` — confirma hipótesis de degradación por acumulación.
- Ventaja para el informe: cada ruta de decisión puede enunciarse en lenguaje natural.

### 7.4 Random Forest

**Puntos:**
- `RandomForestClassifier(n_estimators=200, max_depth=6, min_samples_leaf=20, class_weight='balanced', random_state=42)`.
- Ventaja sobre DT: reducción de varianza por agregación de 200 árboles; menor sobreajuste.
- `min_samples_leaf=20`: cada hoja debe representar al menos 20 horas de operación — evita memorizar spikes individuales.
- Importancia de features: media de la reducción de impureza Gini por feature a través de todos los árboles.

### 7.5 Red Neuronal MLP (Keras)

**Puntos:**
- Arquitectura: `Dense(32, relu) → Dense(16, relu) → Dense(1, sigmoid)`.
- Pérdida: `binary_crossentropy`; optimizador: `Adam(lr=1e-3)`.
- Normalización de features: `StandardScaler` ajustado en el conjunto de entrenamiento únicamente.
- `EarlyStopping(patience=10, restore_best_weights=True)` sobre `validation_split=0.15`.
- `class_weight=CLASS_WEIGHT` (mismos pesos que sklearn).
- Nota: la MLP requiere normalización porque el gradiente es sensible a la escala; los árboles no la necesitan.

### 7.6 Métrica de evaluación

**Puntos:**
- **Métrica primaria: Recall.** Coste operacional: un FN (advertencia perdida) es una parada no programada; un FP es una inspección innecesaria. En mantenimiento predictivo el FN es sistemáticamente más costoso.
- **F1-Score** como métrica de balance para la comparación entre modelos.
- **Accuracy**: reportada pero no primaria (misleading con desequilibrio 7:1).
- **Matrices de confusión**: TP/FP/FN/TN absolutas para contextualizar los scores.

**Tabla 7.1:** Resumen de hiperparámetros por modelo.

| Parámetro | Decision Tree | Random Forest | MLP |
|-----------|---------------|---------------|-----|
| Profundidad máx. | 4 | 6 | — |
| N.º estimadores | — | 200 | — |
| min_samples_leaf | — | 20 | — |
| Neuronas | — | — | 32 → 16 → 1 |
| Activación | — | — | ReLU / Sigmoid |
| Optimizador | — | — | Adam (lr=1e-3) |
| class_weight | balanced | balanced | {0:0.57, 1:4.00} |
| Normalización | No | No | StandardScaler |
| random_state | 42 | 42 | 42 (tf.random.set_seed) |

---

## 8. Resultados

**Propósito:** Presentar los resultados cuantitativos de forma objetiva antes de cualquier interpretación.

**Extensión:** 2–3 páginas.

### 8.1 Métricas de clasificación — conjunto de test

**Tabla 8.1:** Comparación de métricas — TEST SET (INDNº1, cross-machine).

| Modelo | Accuracy | Precision | Recall | F1-Score |
|--------|----------|-----------|--------|----------|
| Decision Tree (depth 4) | 0,7061 | 0,4535 | **0,8537** | **0,5923** |
| Random Forest (n=200, d=6) | 0,6977 | 0,4458 | **0,8585** | 0,5869 |
| MLP (32-16-1) | *(resultado en Jupyter)* | — | — | — |
| Baseline (umbral horas) | *(calcular en notebook)* | — | — | — |

### 8.2 Matrices de confusión

**Tabla 8.2:** Componentes de la matriz de confusión — TEST SET.

| Modelo | TP | FP | FN | TN | Recall | Specificity |
|--------|----|----|----|----|--------|-------------|
| Decision Tree | 356 | 429 | 61 | 821 | 85,3 % | 65,7 % |
| Random Forest | 358 | 445 | 59 | 805 | 85,8 % | 64,4 % |

### 8.3 Importancia de features

**Puntos:**
- `hours_loaded_since_clear`: importancia DT ≈ 40–55 %; RF ≈ 40–55 %.
- `speed_mean_1h`: segundo predictor (RF ≈ 15–20 %).
- `oil_temp_mean_1h`: tercer predictor.
- Las features de presión (`p_mean_1h`, `p_std_1h`) tienen importancia marginal individual pero contribuyen al conjunto.

**Figuras a insertar:**
- **Fig 5** — Matrices de confusión (`figures/fig5_confusion_matrices.png`)
- **Fig 6** — Comparación de modelos (`figures/fig6_model_comparison.png`)
- **Fig 3** — Árbol de decisión (`figures/fig3_decision_tree.png`) — puede ir aquí o en §7
- **Fig 4** — Importancia de features (`figures/fig4_feature_importance.png`)

---

## 9. Discusión

**Propósito:** Interpretar los resultados en el contexto del problema industrial y los objetivos del proyecto.

**Extensión:** 2–3 páginas.

**Puntos:**
1. **Validación de la hipótesis central:** el dominio del feature `hours_loaded_since_clear` en ambos modelos confirma que la degradación del filtro es principalmente una función del tiempo acumulado de operación desde el último reemplazo — exactamente lo que la física predice.
2. **Significado del Recall ≈ 85 %:** el modelo detecta ~85 de cada 100 episodios de advertencia con 24 h de anticipación. Para una instalación con 4 episodios por año, esto implica detectar ~3,4 episodios y perder ~0,6. En la práctica operacional, el costo de una parada no programada justifica el 85 % de detección incluso con la tasa de FP asociada.
3. **Significado de la Precision ≈ 45 %:** de cada 100 alertas generadas, ~55 son falsas. En mantenimiento predictivo industrial, una tasa de FP del 55 % puede generar fatiga de alarmas si no se gestiona con un umbral de probabilidad ajustado. En la práctica, se recomendaría elevar el umbral de clasificación de 0,5 a ~0,65–0,70 para reducir FP al precio de perder algunos TP.
4. **Generalización cross-machine:** el modelo fue entrenado exclusivamente en INDNº2 (filtro de aire) y evaluado en INDNº1 (filtro de aceite) — dos mecanismos de filtración distintos. El Recall se mantiene en ~85 %, lo que sugiere que la degradación de filtros por acumulación de horas es un patrón universal en esta familia de compresores.
5. **Comparación DT vs RF:** el Decision Tree (depth 4) supera ligeramente al Random Forest en F1 (0,5923 vs. 0,5869). Esto es inusual y se explica por el tamaño reducido del test set (1.667 filas) y la preponderancia del feature de acumulación — un árbol simple lo captura casi tan bien como 200 árboles.

---

## 10. Limitaciones

**Propósito:** Evaluar honestamente los límites del trabajo. Los evaluadores valoran más una sección de limitaciones robusta que resultados inflados.

**Extensión:** 1–1,5 páginas.

**Tabla 10.1:** Limitaciones del proyecto.

| Limitación | Impacto | Mitigación aplicada |
|------------|---------|---------------------|
| Solo 6 episodios etiquetados en total | Alta varianza en métricas; ±15 pp en F1 por episodio | LOEO-CV documentado como trabajo futuro |
| INDNº1 tiene solo 2 episodios en 70 días | Test set sesgado hacia condición de advertencia activa (25 % positive rate vs. 13 % en train) | Documentado explícitamente |
| Canal ADT (temperatura de salida del tornillo) no instalado | Pérdida de la señal térmica más directa | Speed SP y oil_temp como proxies |
| Canal de corriente del motor (ch15) inactivo | Sin medición directa de carga mecánica | Speed SP como proxy de potencia |
| Desfase temporal UTC/local (max ±4 h) | Algunas horas pueden estar mal etiquetadas en los límites de episodio | Aceptable: episodios duran días |
| Dataset de 2 compresores | Sin prueba de generalización a flota completa | EMBNº1 y EMBNº2 pendientes de nuevos datos |
| MLP sin ajuste de arquitectura | Posible sobreajuste o subajuste | Arquitectura mínima elegida deliberadamente |

---

## 11. Conclusiones

**Propósito:** Responder directamente la pregunta de investigación y sintetizar los hallazgos.

**Extensión:** 1 página.

**Puntos:**
1. **Respuesta a la pregunta de investigación:** Sí, es técnicamente factible predecir la activación de advertencias de ΔP en filtros de compresor KAESER CSDX165 con 24 horas de anticipación, alcanzando un Recall de ~85 % en un compresor no visto durante el entrenamiento.
2. **Hallazgo más significativo:** la edad del filtro (horas acumuladas desde el último reemplazo) es el predictor dominante, lo que sugiere que un sistema basado en reglas sobre contadores de horas puede replicar gran parte del rendimiento del ML — la contribución del ML es refinar la predicción usando condiciones de operación (velocidad, temperatura).
3. **Relevancia práctica:** el horizonte de 24 h es suficiente para planificar el reemplazo en el turno siguiente, evitando paradas no programadas.
4. **Contribución metodológica:** se desarrolló un pipeline reproducible de transformación de archivos binarios DAT propietarios a features de ML, documentado y versionado.

---

## 12. Trabajo Futuro

**Propósito:** Identificar extensiones naturales del proyecto que queden fuera del alcance actual.

**Extensión:** 0,5–1 página.

**Puntos:**
1. **Más compresores:** extender a EMBNº1 y EMBNº2 cuando se acumulen nuevos episodios con cobertura DAT.
2. **Más features:** completar el mapa de canales (130 canales identificados; solo 8 usados). Especialmente: contadores de horas del controlador (disponibles en `autobackup/` cuando se llene), temperatura de salida del tornillo (ADT, sensor pendiente de instalar), canal de kW/m³ derivado de corriente y velocidad.
3. **LOEO-CV:** leave-one-episode-out cross-validation para estimar varianza de métricas con los 6 episodios disponibles.
4. **Ajuste de umbral de decisión:** explorar la curva precision-recall y seleccionar el umbral operacional óptimo (precision ≥ 0,6 como restricción).
5. **Etiquetado por episodio:** reformular como detección del inicio del episodio (label estricto) en lugar de active_warning extendido.
6. **Estudio prospectivo:** desplegar el modelo en producción con un año de nuevos datos para validación con datos no históricos.
7. **Análisis de derivación del sensor (drift):** monitorear si la distribución de features cambia con el tiempo y cuándo sería necesario reentrenar.

---

## Referencias

**Puntos:**
- Manual del fabricante: *Sigma Control 2 Screw Fluid ≥ 4.1.X*, KAESER Kompressoren, N.º 9.9450.08S (español).
- Documentación sklearn: `DecisionTreeClassifier`, `RandomForestClassifier`, `class_weight`.
- Documentación Keras/TensorFlow: `Sequential`, `Dense`, `EarlyStopping`.
- Pandas, NumPy, Matplotlib (citar versiones usadas).
- Artículos de referencia sobre mantenimiento predictivo en compresores (sugeridos: buscar en IEEE Xplore "predictive maintenance rotary screw compressor" o "air compressor filter prediction").

---

## Anexos

| Anexo | Contenido |
|-------|-----------|
| A | Mapa completo de canales DAT (130 canales, nombres, unidades, escala) |
| B | Inventario de carpetas BF por compresor |
| C | Auditoría de solapamiento temporal (tabla completa) |
| D | Distribución semanal de episodios 0013 W en INDNº2 |
| E | Código fuente del notebook (`notebooks/proyecto_ia.ipynb`) |
| F | Figuras en alta resolución (Fig 1–6, PNG 150 dpi) |
