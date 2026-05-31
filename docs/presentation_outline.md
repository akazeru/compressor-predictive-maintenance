# Presentación de Proyecto — Esquema Diapositiva a Diapositiva
## Mantenimiento Predictivo en Compresores Industriales KAESER CSDX165

> **Duración objetivo:** 15–20 minutos + 5 minutos de preguntas  
> **Total de diapositivas:** 14  
> **Formato recomendado:** 16:9, fuente mínima 20 pt en contenido, 28 pt en títulos  
> **Figuras fuente:** `figures/` (PNG 150 dpi — importar directamente a PPT)

---

## Slide 1 — Portada

**Título:**  
Predicción de Advertencias de Diferencial de Presión en Filtros  
de Compresores Rotativos de Tornillo Mediante Aprendizaje Automático

**Subtítulo:** Proyecto Final — Curso de Inteligencia Artificial Industrial

**Contenido visual:**
- Foto del compresor KAESER CSDX165 (imagen del fabricante o del sitio industrial)
- Logotipo de la institución

**Elementos:**
- Autor, fecha (mayo 2026)
- Leyenda discreta: *"Dataset: 9.745 horas-máquina · 6 episodios etiquetados · 2 compresores"*

**Puntos de presentación:**
- *"Este proyecto aborda un problema real de mantenimiento industrial: predecir cuándo un filtro de compresor va a generar una advertencia de presión, antes de que ocurra."*
- *"El objetivo es darle al operador 24 horas de anticipación para planificar el cambio del filtro en el turno siguiente, sin parar la producción."*

---

## Slide 2 — Contexto Industrial

**Título:** El problema: filtros que se saturan sin aviso

**Contenido:**
- Diagrama simplificado: compresor → filtro de aceite/aire → actuador → red de aire comprimido
- Dos íconos: filtro limpio (verde) / filtro saturado (rojo) con flecha mostrando ΔP creciente
- Recuadro destacado: *"Un filtro saturado = parada no programada = pérdida de producción"*

**Tabla small (puede ser texto en dos columnas):**
| Evento | Código | Tipo de filtro |
|--------|--------|----------------|
| Oil Filter ΔP ↑ | 0011 W | Aceite |
| Air Filter ΔP ↑ | 0013 W | Aire |

**Puntos de presentación:**
- *"La planta tiene 4 compresores KAESER CSDX165. Cada uno tiene un filtro de aceite y un filtro de aire. Cuando el diferencial de presión supera el umbral de fábrica, el controlador genera una advertencia."*
- *"El problema: la advertencia es binaria. No hay sensor analógico que me diga 'el filtro está al 70 % de saturación'. Por eso se necesita ML."*
- *"Si el operador no cambia el filtro a tiempo, el compresor puede parar en plena producción."*

---

## Slide 3 — Pregunta de Investigación y Objetivo

**Título:** ¿Qué queremos predecir?

**Contenido central (puede ser un diagrama de línea de tiempo):**
```
[Hora 0]  [Hora t-24]  [Hora t]         [Episodio activo]
   │             │         │                    │
  Normal     PREDECIR   Filtro satura     Warning activa
             aquí ↑
```

**Texto:** *"¿Podemos predecir la activación de la advertencia 24 horas antes, usando solo los datos del propio controlador?"*

**Tres restricciones clave (iconos + texto):**
1. Sin sensor de ΔP continuo — solo un switch binario
2. Solo 2 compresores con datos alineados (evento + sensor)
3. Generalización obligatoria: entrenar en un compresor, probar en otro

**Puntos de presentación:**
- *"El horizonte de 24 horas no es arbitrario. Es el tiempo mínimo para planificar una mantención durante el turno siguiente sin interrumpir la producción."*
- *"La restricción más importante: el ΔP del filtro NO está disponible como señal continua. El controlador solo registra 'filtro OK' o 'filtro saturado'. Todo lo que tenemos son señales indirectas."*

---

## Slide 4 — Los Datos

**Título:** Fuentes de datos: 9.745 horas de operación industrial

**Contenido (dos columnas):**

Columna izquierda — *Grabador de datos (.dat)*:
- 1 archivo/hora, 954.664 bytes binario
- 3.600 registros × 130 canales int16 a 1 Hz
- INDNº1: 1.675 h | INDNº2: 8.070 h

Columna derecha — *Log de eventos (.txt)*:
- Timestamped events del controlador SIGMA CONTROL 2
- INDNº1: 2 episodios 0011 W in-DAT
- INDNº2: 4 episodios 0013 W in-DAT

**Tabla:**
| Compresor | Filtro | Horas DAT | Episodios | Rol en ML |
|-----------|--------|-----------|-----------|-----------|
| INDNº1 | Aceite | 1.675 | 2 | **Test** |
| INDNº2 | Aire | 8.070 | 4 | **Train** |

**Puntos de presentación:**
- *"Los archivos .dat son binarios propietarios de KAESER. El primer paso del proyecto fue construir el parser desde cero."*
- *"Solo estos dos compresores tienen episodios de advertencia dentro del rango temporal de los sensores. Los otros dos están excluidos porque sus eventos ocurrieron antes de que empezara la grabación de datos."*
- *"El diseño del experimento es natural: los 4 episodios de INDNº2 son el entrenamiento, y el test es INDNº1 — un compresor distinto con un filtro de un tipo diferente."*

---

## Slide 5 — Pipeline de Datos

**Título:** De archivos binarios a dataset supervisado

**Contenido:** Diagrama de flujo horizontal (6 pasos):

```
[Archivos .dat]  →  [read_dat_hour()]  →  [extract_hourly_stats()]
                                                     ↓
[df_dataset]  ←  [assign_zones()]  ←  [build_feature_matrix()]
     ↑
[CompressorMsgs.txt]  →  [parse_event_log()]  →  [build_episode_table()]
```

**Métricas del pipeline:**
- Tiempo de procesamiento: INDNº1 ≈ 14 s, INDNº2 ≈ 66 s
- Salida: DataFrame 9.745 × 12

**Puntos de presentación:**
- *"Todo el pipeline corre en el notebook de manera reproducible. No hay pasos manuales ni archivos intermedios."*
- *"El join entre sensor y evento se hace por timestamp. Hay un desfase de hasta 4 horas entre el reloj del DAT (UTC) y el log de eventos (hora local chilena), pero es aceptable porque los episodios duran días."*

---

## Slide 6 — Features y Etiquetas

**Título:** 8 features + 4 zonas de etiquetado

**Contenido (dos columnas):**

Columna izquierda — *Features MVP*:
| # | Feature | Proxy de |
|---|---------|---------|
| 1 | `p_mean_1h` | Carga de red |
| 2 | `p_std_1h` | Ciclos carga/descarga |
| 3 | `oil_temp_mean_1h` | Estrés térmico |
| 4 | `oil_temp_max_1h` | Pico térmico |
| 5 | `speed_mean_1h` | Caudal volumétrico |
| 6 | `speed_std_1h` | Estabilidad operacional |
| 7 | `load_frac_1h` | Tiempo efectivo filtrado |
| **8** | **`hours_loaded_since_clear`** | **Edad del filtro ← CLAVE** |

Columna derecha — *Zonas*:
- 🟢 Negativo — operación normal
- 🟡 Pre-advertencia — 24 h previas al episodio **(etiqueta = 1)**
- 🔴 Advertencia activa — episodio en curso **(etiqueta = 1)**
- ⚫ Recuperación — 4 h post-cambio (excluida)

**Puntos de presentación:**
- *"La feature más importante antes de entrenar cualquier modelo es la número 8: las horas acumuladas desde el último cambio de filtro. Esta variable codifica directamente la 'edad' del filtro."*
- *"La etiqueta es extendida: incluye tanto la pre-advertencia como la advertencia activa como positivos. Esto da un ratio de clase de 5:1, manejable con class_weight."*

---

## Slide 7 — Línea de Tiempo (Fig 2)

**Título:** Los episodios vistos en el tiempo

**Figura a mostrar:** `figures/fig2_episode_timeline.png` (ocupa toda la diapositiva)

**Leyenda reducida debajo de la figura:**
*"Cada banda ámbar = 24 h de pre-advertencia (etiqueta positiva). Cada banda roja = episodio activo. Franjas verdes = operación normal."*

**Puntos de presentación:**
- *"Este gráfico muestra el 'cuándo' del problema. Los episodios de INDNº2 están bien separados — un ciclo de 3 a 4 meses entre cambios de filtro. Exactamente lo que el fabricante recomienda."*
- *"INDNº1 tiene sus episodios concentrados en las últimas semanas del rango DAT, lo que hace el test más exigente: el modelo nunca vio este compresor."*
- *"La brecha entre episodios es nuestro conjunto de datos negativos. Son los periodos donde el filtro está limpio y funcionando correctamente."*

---

## Slide 8 — Modelos Aplicados

**Título:** Tres modelos, una decisión de diseño común

**Contenido:**
Tres columnas, un modelo cada una:

**Decision Tree**
- Profundidad máx.: 4
- Interpretable al 100 %
- Rol: baseline + transparencia

**Random Forest**
- 200 árboles, depth 6
- Reducción de varianza
- Rol: modelo principal

**MLP (Keras)**
- Dense 32 → 16 → 1 (sigmoid)
- Normalización: StandardScaler
- Rol: benchmark NN

**Decisión común a los tres:**
- `class_weight='balanced'` → pesos {0: 0,57, 1: 4,0}
- Train: INDNº2 | Test: INDNº1
- Sin tuning avanzado (fiel al alcance del proyecto)

**Puntos de presentación:**
- *"Los tres modelos comparten la misma estrategia de desequilibrio de clases: class_weight balanced. Esto evita que el modelo simplemente prediga siempre 'negativo' para tener alta accuracy."*
- *"El Decision Tree es el más valioso para la defensa: puedo mostrar exactamente qué regla está aplicando en cada nodo. Es el modelo que le mostraría a un operador de planta."*

---

## Slide 9 — El Árbol de Decisión (Fig 3)

**Título:** Lo que aprendió el árbol

**Figura a mostrar:** `figures/fig3_decision_tree.png` (mostrar versión completa; si es muy pequeña en PPT, recortar los primeros 2 niveles)

**Recuadro superpuesto (fuera de la figura):**
*"División raíz: `hours_loaded_since_clear` ← la edad del filtro es el predictor número 1"*

**Puntos de presentación:**
- *"La primera pregunta que hace el árbol es: '¿Las horas acumuladas desde el último cambio de filtro superan X horas?'. Si sí, entra en zona de riesgo."*
- *"Esto valida la hipótesis física: el filtro se ensucia en función del tiempo de operación desde el último reemplazo. No es magia — es física del filtrado."*
- *"Las ramas secundarias usan temperatura y velocidad para afinar. Un filtro viejo que además opera a alta temperatura y alta velocidad tiene mayor probabilidad de advertencia inminente."*

---

## Slide 10 — Importancia de Features (Fig 4)

**Título:** ¿Qué variables importan y por qué?

**Figura a mostrar:** `figures/fig4_feature_importance.png`

**Texto a la derecha de la figura:**
- `hours_loaded_since_clear` ≈ 40–55 % → **Edad del filtro**
- `speed_mean_1h` ≈ 15–20 % → **Mayor velocidad = mayor caudal**
- `oil_temp_mean_1h` ≈ 10–15 % → **Temperatura = degradación del aceite**
- Resto de features: contribución marginal individual

**Puntos de presentación:**
- *"El resultado es consistente entre el Decision Tree y el Random Forest — los dos modelos independientes coinciden en el ranking de importancia."*
- *"Esto es más que un número estadístico. La importancia del feature de acumulación nos dice que la frecuencia del cambio de filtro debería estar guiada por horas de operación real, no por el calendario."*
- *"Si el compresor estuvo parado durante 2 semanas, el contador no avanza. El filtro no se ensucia cuando no filtra."*

---

## Slide 11 — Resultados: Matrices de Confusión (Fig 5)

**Título:** ¿Cuántas advertencias detectamos?

**Figura a mostrar:** `figures/fig5_confusion_matrices.png`

**Texto resumen debajo:**

| | Decision Tree | Random Forest |
|--|--|--|
| **Recall (TP/P)** | **85,4 %** | **85,8 %** |
| Falsos Negativos | 61 | 59 |
| Falsos Positivos | 429 | 445 |

**Mensaje clave (recuadro):** *"~85 de cada 100 horas de advertencia son detectadas con 24 h de anticipación"*

**Puntos de presentación:**
- *"El número que importa para operaciones es el Recall: detectamos el 85 % de todas las horas de advertencia en un compresor que el modelo nunca vio durante el entrenamiento."*
- *"Los 61 Falsos Negativos son las horas de advertencia que el modelo no detectó. En el peor caso, esto es el inicio de un episodio breve (como el episodio 10 de INDNº1, que duró solo 4 horas)."*
- *"Los 429 Falsos Positivos son alarmas que se generarían sin que hubiera una advertencia real. Es el costo operacional del sistema — un operador recibiría ~18 falsas alarmas por mes en promedio."*
- *"Para producción, se ajustaría el umbral de decisión de 0,5 a 0,65–0,70 para reducir las falsas alarmas a costa de perder algunos TP."*

---

## Slide 12 — Comparación Final de Modelos (Fig 6)

**Título:** Comparación de modelos

**Figura a mostrar:** `figures/fig6_model_comparison.png`

**Tabla de resultados (extraída de §8):**
| Modelo | Accuracy | Precision | Recall | F1 |
|--------|----------|-----------|--------|-----|
| Decision Tree | 0,706 | 0,454 | **0,854** | **0,592** |
| Random Forest | 0,698 | 0,446 | **0,859** | 0,587 |

**Conclusión visual:** Las barras de Recall (el criterio industrial más relevante) son prácticamente idénticas entre los dos modelos.

**Puntos de presentación:**
- *"Algo sorprendente: el árbol de decisión simple con 4 niveles tiene un F1 levemente superior al Random Forest con 200 árboles. Esto es inusual en ML, pero se explica por la dominancia del feature de acumulación — un árbol simple lo captura casi perfectamente."*
- *"Para este problema y este tamaño de dataset, la complejidad adicional del Random Forest no aporta beneficio mensurable. El árbol de decisión es suficiente — y es explicable a cualquier técnico de mantenimiento."*
- *"La MLP se reporta en el notebook; los resultados dependerán de si TensorFlow está instalado en el entorno de Jupyter."*

---

## Slide 13 — Limitaciones

**Título:** Qué sí y qué no podemos concluir

**Contenido:** Dos columnas:

**Sí podemos concluir:**
- ✅ La predicción es factible con Recall ~85 %
- ✅ La edad del filtro es el predictor dominante
- ✅ El modelo generaliza entre compresores
- ✅ El horizonte de 24 h es operacionalmente útil

**No podemos concluir (todavía):**
- ❌ Rendimiento con más de 6 episodios disponibles
- ❌ Precisión > 50 % sin ajuste de umbral
- ❌ Generalización a flotas de otras marcas
- ❌ Desempeño bajo distribución cambiante (drift)

**Puntos de presentación:**
- *"Ser honesto sobre las limitaciones es parte del método científico. Con solo 6 episodios etiquetados, las métricas tienen una varianza alta — si hay un episodio difícil de predecir en el test set, el F1 puede variar ±15 puntos porcentuales."*
- *"El proyecto es una prueba de concepto sólida, no un sistema listo para producción. Lo próximo sería un estudio prospectivo con 12 meses de datos nuevos."*

---

## Slide 14 — Conclusiones y Trabajo Futuro

**Título:** Qué logramos y qué sigue

**Contenido (dos secciones):**

**Conclusiones:**
1. Es factible predecir advertencias de ΔP en filtros de compresor con 24 h de anticipación (Recall ≈ 85 % cross-machine)
2. La edad del filtro (`hours_loaded_since_clear`) es el predictor dominante — la física del filtrado está capturada en los datos
3. Se construyó un pipeline reproducible de 9.745 horas de datos binarios industriales → DataFrame supervisado
4. El Decision Tree ofrece el mejor balance entre rendimiento e interpretabilidad para este dataset

**Trabajo futuro:**
- Expandir a EMBNº1/EMBNº2 cuando haya nuevos episodios con cobertura DAT
- LOEO-CV para estimar varianza de métricas
- Optimización del umbral de decisión para producción
- Estudio prospectivo de 12 meses

**Puntos de presentación:**
- *"La conclusión principal no es que el modelo funciona al 85 %. La conclusión principal es que con 8 features simples derivadas del propio controlador, sin instalar ningún sensor adicional, es posible anticipar el mantenimiento de filtros."*
- *"El siguiente paso práctico no es más ML — es desplegar el pipeline en un servidor que procese los archivos .dat automáticamente y genere alertas para el equipo de mantenimiento."*
- *"Gracias. Preguntas."*

---

## Notas de Diseño Visual

### Paleta de colores recomendada

| Elemento | Color | Hex |
|----------|-------|-----|
| Color primario (títulos, énfasis) | Azul oscuro | `#1565C0` |
| INDNº1 (compresor aceite) | Azul | `#1565C0` |
| INDNº2 (compresor aire) | Naranja oscuro | `#E65100` |
| Zona negativo | Verde | `#4CAF50` |
| Zona pre-advertencia | Ámbar | `#FFC107` |
| Zona advertencia activa | Rojo | `#F44336` |
| Fondo de diapositivas | Blanco | `#FFFFFF` |
| Texto secundario | Gris oscuro | `#37474F` |

### Tamaños de fuente mínimos

- Títulos de diapositiva: 28 pt
- Texto de cuerpo: 20 pt
- Leyendas de figura: 16 pt
- Texto en tablas: 16 pt

### Importación de figuras

Todas las figuras están en `figures/` (PNG, 150 dpi). Para importar:
- PowerPoint: *Insertar → Imagen → Desde archivo*
- Mantener proporciones originales (no estirar)
- Usar "Alinear al centro" horizontalmente en la diapositiva
- Para Fig 3 (árbol): usar pantalla completa o recortar a los primeros 2–3 niveles para slides

### Diapositivas de apoyo (backup, no presentar salvo preguntas)

- **Slide B1:** Estructura del archivo `.dat` (tabla offset/tipo/descripción de la cabecera)
- **Slide B2:** Distribución de zonas de etiquetado — Fig 1
- **Slide B3:** Comparación de episodios pre/post deduplicación de clearances
- **Slide B4:** Código clave del pipeline (celdas 13–14 del notebook)
