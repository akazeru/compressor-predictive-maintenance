Let me read the course documents before performing the review.

Good — documents are in `docs curso`. Let me read the course program and all six class slides simultaneously.

Now let me read all six class slides and the labs to map coverage precisely.

Now let me read classes 3 through 6 and the labs.

Now let me read the three most relevant labs — the ones covering ML models.

I now have everything needed for the review. Let me compile the full analysis.

---

## REVISIÓN DE ALINEACIÓN CON EL CURSO
### Proyecto: Mantenimiento Predictivo de Compresores KAESER CSDX165
### Curso: IA Aplicada a la Industria — USACH, Semestre 1, 2026

---

## Mapa de cobertura del curso (estado al 30/05/2026)

| Clase | Fecha | Contenido cubierto |
|---|---|---|
| 1 | 15 abr | Introducción a la IA, Google Colab, ML como concepto, Árbol de Decisión y Regresión Lineal introducidos conceptualmente |
| 2 | 22 abr | Bases de datos, limpieza de datos CSV, calidad de datos |
| 3 | 29 abr | Features X/y, One-Hot Encoding, Min-Max Scaling, Train/Test Split (80/20 aleatorio) |
| 4 | 6 may | Taxonomía del AA (supervisado/no supervisado), clasificación vs. regresión, clustering, Bias/Varianza, parámetros vs. hiperparámetros |
| 5 | 20 may | Pipeline completo de ML (caso SECOM), NaN, desequilibrio de clases, Precision/Recall/F1, selección de features (varianza, correlación, Feature Importance con RF), PCA |
| 6 | 27 may | El Perceptrón: anatomía (pesos, bias, activación), funciones Step/Sigmoide/ReLU, regla de aprendizaje, limitación XOR, intro a MLP multicapa (**próxima clase**) |

**Labs ejecutados:** Lab 1 (Colab), Lab 2 (limpieza), Lab 3 (preparación datos), Lab 4 (DT + Regresión Lineal; RF como actividad **opcional**), Lab 5 (Perceptrón único con Keras: `Dense(1, sigmoid)`), Lab 6 (MLP multiclase: `Dense(16,relu)→Dense(12,relu)→Dense(3,softmax)`)

**Nota crítica sobre la metodología del curso:** El programa define el Proyecto Final como *"análisis de un caso industrial, interpretación de resultados de modelos entregados en Python, roadmap estratégico."* Los labs tienen código Python **ya provisto por el docente**; el foco es **interpretar resultados, no programar desde cero**. Este proyecto excede esa expectativa de forma sustancial.

---

## 1. Alineado con el curso

Los siguientes componentes del proyecto corresponden directamente al contenido cubierto:

**Completamente alineados:**

- **Clasificación binaria supervisada** — Concepto central de Clases 1, 3, 4 y 5.
- **`DecisionTreeClassifier(max_depth=4)`** — El Lab 4 usa exactamente este modelo con exactamente este hiperparámetro. Es el ejemplo canónico del curso.
- **Train/test split** — Clase 3 y Lab 3 lo cubren explícitamente. El proyecto usa una variante diferente (cross-machine en lugar de 80/20 aleatorio), pero el concepto es el mismo.
- **Recall como métrica primaria sobre Accuracy** — Este es el hallazgo central de la Clase 5 (Paradoja de la Exactitud con SECOM) y el argumento del costo asimétrico FN > FP. El proyecto lo argumenta exactamente en el mismo lenguaje.
- **Precision, Recall y F1-Score** — Cubiertos con fórmulas en Clase 5. El proyecto los reporta correctamente.
- **Desequilibrio de clases como problema** — Clase 5 dedica dos diapositivas al tema. El proyecto lo identifica y lo gestiona.
- **Feature Importance con Random Forest** — Aparece en Clase 5 como uno de los tres métodos de selección de características. El proyecto lo usa como herramienta de análisis.
- **Matriz de confusión** — Clase 5 la introduce con la misma terminología TP/FP/FN/TN.
- **Parámetros vs. hiperparámetros** — Clase 4. El proyecto discute `max_depth`, `n_estimators` y `min_samples_leaf` como hiperparámetros elegidos por el ingeniero.
- **Bias/Varianza y riesgo de overfitting** — Clase 4. El proyecto argumenta `max_depth=4` y `min_samples_leaf=20` como medidas anti-overfitting, lenguaje completamente alineado.
- **MLP como arquitectura** — Lab 6 cubre MLP multicapa con Keras (`Dense(relu)→Dense(softmax)`). El proyecto usa una estructura análoga para clasificación binaria.
- **Funciones de activación ReLU y Sigmoide** — Clase 6 las cubre con fórmulas y gráficos.
- **Optimizador Adam, binary_crossentropy** — Lab 5 y Lab 6 usan exactamente estos en `model.compile()`.
- **Preparación de datos (NaN, imputación)** — Clases 2, 3, 5.

---

## 2. Potencialmente más avanzado que el contenido del curso

Los siguientes componentes están parcialmente cubiertos o van más allá de lo que el curso enseña explícitamente:

### 2.1 — Random Forest como modelo principal · **Nivel: Moderadamente avanzado**

**Situación:** En el curso, el Random Forest aparece una sola vez, en Clase 5, como herramienta de selección de features. En Lab 4, entrenarlo como clasificador es una **actividad voluntaria**. No existe ninguna clase ni lab donde el RF sea el modelo principal de un pipeline de evaluación.

**Impacto:** El estudiante puede mostrar el RF y sus métricas, pero no puede justificar en profundidad por qué 200 árboles reducen la varianza ni explicar el mecanismo de *bagging* con vocabulario del curso.

**Recomendación:** Presentarlo siempre como *"extensión del árbol de decisión del curso"* y anclar la discusión en lo que el curso sí cubre: feature importance y el concepto de bias/varianza.

---

### 2.2 — `class_weight='balanced'` · **Nivel: No cubierto**

**Situación:** La Clase 5 enseña que con clases desbalanceadas hay que usar Recall en lugar de Accuracy. La **solución al desbalanceo en el código** que el curso muestra es solo ajustar la métrica de evaluación, no los pesos de entrenamiento. El parámetro `class_weight='balanced'` no aparece en ningún lab ni en ninguna diapositiva.

**Impacto:** Pregunta casi segura en una defensa oral: *"¿Por qué usaste class_weight='balanced'?"* El estudiante necesita explicar la fórmula $w_c = \frac{n}{n_c \times 2}$ o la idea de penalización, conceptos no enseñados.

**Recomendación:** En el informe y la presentación, anclar la justificación en el lenguaje del curso: *"Para que el modelo no ignore la clase minoritaria por la paradoja de la exactitud estudiada en el curso."* Evitar citar la fórmula exacta de los pesos a menos que se pueda defender.

---

### 2.3 — División cross-machine temporal en lugar de split aleatorio · **Nivel: Avanzado**

**Situación:** El curso enseña exclusivamente `train_test_split(X, y, test_size=0.2)` — división aleatoria, 80/20. El concepto de preservar integridad temporal, evitar data leakage y evaluar generalización cross-machine no aparece en ninguna clase ni lab.

**Impacto:** Un evaluador puede preguntar: *"¿Por qué no hiciste un split aleatorio como en los labs?"* La respuesta correcta (evitar contaminar el futuro con el pasado en datos temporales) requiere entendimiento de conceptos no cubiertos en el curso.

**Recomendación:** Explicarlo siempre en lenguaje del bias/varianza: *"Un split aleatorio habría creado overfitting a este compresor específico. Para probar que el modelo generaliza —como se estudió en el tradeoff bias/varianza— evaluamos en un equipo completamente distinto."* Este puente al vocabulario del curso es sólido.

---

### 2.4 — Pipeline de parseo de archivos DAT binarios · **Nivel: Muy avanzado / fuera del alcance del curso**

**Situación:** El curso usa exclusivamente archivos CSV cargados con `pd.read_csv()`. El parseo de archivos binarios con `np.frombuffer()`, manejo de offsets de cabecera, decodificación `int16 little-endian` y conversión de timestamps Unix son conceptos de programación de bajo nivel completamente fuera del alcance del curso. El programa dice explícitamente: *"Ejecutarán código Python ya desarrollado en Google Colab. El foco es interpretar resultados."*

**Impacto:** Si un evaluador pregunta *"¿Cómo cargaste los datos?"*, la descripción técnica del pipeline no puede ser defendida con el vocabulario del curso. Además, el código fue desarrollado manualmente, contradiciendo la metodología del curso.

**Recomendación para la defensa:** Describir este componente en términos de ingeniería de datos, no de programación: *"Los datos estaban en un formato binario propietario del controlador. Desarrollé un script de conversión que transforma esos archivos al formato tabular estándar (DataFrame) que los modelos del curso requieren. Este script actúa como el paso de limpieza y preparación de datos del pipeline."*

---

### 2.5 — Ingeniería de la característica `hours_loaded_since_clear` · **Nivel: Avanzado**

**Situación:** El curso cubre One-Hot Encoding y Min-Max Scaling como transformaciones de features. La construcción de una variable acumulativa de dominio específico a partir de un log de eventos externos requiere conocimiento de dominio industrial y lógica de barrido temporal — no cubiertos en el curso.

**Impacto:** Es la feature más importante del modelo. Si el evaluador pregunta cómo se construyó, la respuesta es técnica y compleja.

**Recomendación:** Enmarcarla siempre desde la hipótesis física: *"Aplicamos el conocimiento de dominio industrial para crear una variable que representa la 'edad' del filtro. En el curso aprendimos que las features deben representar el fenómeno físico que queremos predecir. Esta es la más directa de todas."*

---

### 2.6 — `EarlyStopping` con `restore_best_weights` · **Nivel: No cubierto**

**Situación:** Lab 5 usa `model.fit(epochs=20)` y Lab 6 usa `epochs=40` sin condición de parada. `EarlyStopping` como callback no aparece en ningún lab ni clase.

**Impacto:** Bajo. Se puede describir como *"el entrenamiento se detiene automáticamente cuando el modelo deja de mejorar, para evitar overfitting"* — directamente conectado al concepto de Bias/Varianza de Clase 4.

---

### 2.7 — `StandardScaler` para la MLP vs. `MinMaxScaler` enseñado · **Nivel: Leve**

**Situación:** El curso enseña Min-Max Scaling en Clase 3 con la fórmula explícita. `StandardScaler` (estandarización Z) no se menciona en clase. Lab 4 lo sugiere como actividad voluntaria.

**Impacto:** Bajo. Ambos son métodos de normalización; la distinción es técnica. Se puede decir: *"Usamos una variante de escalado estándar para que las redes neuronales funcionen correctamente, ya que son sensibles a la escala de las variables — concepto introducido en Clase 3."*

---

### 2.8 — Impureza de Gini y MDI como mecanismo interno · **Nivel: Moderado**

**Situación:** El curso explica el árbol de decisión con la analogía del diagrama de flujo y muestra su uso en sklearn, pero **no explica Gini impurity ni cómo el árbol elige la mejor variable**. La Clase 5 muestra Feature Importance visualmente pero no explica el mecanismo MDI.

**Impacto:** El informe actual describe el criterio de Gini en §7.3 y §7.4. Si el evaluador pregunta *"¿qué es la impureza de Gini?"*, el estudiante necesita responder algo no enseñado en el curso.

**Recomendación:** En el informe, simplificar la descripción: *"El árbol selecciona en cada nodo la variable y el umbral que mejor separa las clases positivas de las negativas, usando el criterio estándar de scikit-learn."* Evitar citar "Gini" por nombre en la presentación.

---

## 3. Recommended Simplifications

### Para el informe (§7)

| Párrafo actual | Simplificación recomendada |
|---|---|
| Descripción técnica de la impureza de Gini | Sustituir por: *"El algoritmo selecciona la variable y el umbral que produce la mayor reducción de error en cada nodo, usando el criterio estándar de scikit-learn."* |
| Fórmula de pesos `class_weight='balanced'` | Mantener la fórmula pero añadir un puente explícito al concepto del curso: *"Este ajuste responde directamente a la paradoja de la exactitud estudiada en el curso: sin corrección, el modelo predice siempre la clase mayoritaria."* |
| Descripción de `np.frombuffer` e `int16 LE` | Describir como: *"script de conversión del formato propietario DAT al DataFrame tabular estándar"* — sin detalles de implementación de bajo nivel |
| Descripción del `EarlyStopping` | Simplificar a: *"se detuvo el entrenamiento cuando el error de validación dejó de mejorar, para controlar el sobreajuste"* |
| MDI como mecanismo de importancia | Describir como: *"la importancia refleja cuánto contribuye cada variable a la capacidad de separación del modelo"* — sin citar MDI |

### Para la presentación (slides)

- **No mencionar `class_weight` por nombre en las slides.** Describirlo como: *"Ajuste para que el modelo tome en serio las advertencias poco frecuentes."*
- **No mostrar código DAT en ningún slide principal.** El pipeline de datos se resume en el diagrama de flujo (Slide 5 del outline), no en código.
- **Anclar explícitamente en slides 8 y 9** que los modelos son los *mismos* que en el Lab 4 del curso (árbol de decisión) y su extensión natural (random forest).

---

## 4. Evaluación de la arquitectura MLP

**Veredicto: Aceptable, con un ajuste puntual recomendado.**

| Aspecto | Estado actual | Curso | Evaluación |
|---|---|---|---|
| Arquitectura Dense(32,relu)→Dense(16,relu)→Dense(1,sigmoid) | Proyecto | Lab 6: Dense(16,relu)→Dense(12,relu)→Dense(3,softmax) | ✅ Comparable. La diferencia (más neuronas, binario) es justificable |
| Optimizador Adam | Proyecto | Labs 5 y 6 | ✅ Cubierto |
| `binary_crossentropy` | Proyecto | Lab 5 | ✅ Cubierto |
| `EarlyStopping(patience=10)` | Proyecto | **No cubierto** | ⚠️ Explicar como "control de overfitting", no citar parámetro |
| `StandardScaler` | Proyecto | Actividad voluntaria Lab 4 | ⚠️ Leve. Conectar a "escalado de variables" de Clase 3 |
| `class_weight` en MLP | Proyecto | **No cubierto** | ⚠️ Mismo riesgo que en DT/RF |
| Resultados no verificados fuera de Jupyter | Proyecto | — | ✅ Declarar explícitamente en informe y slides |

**La arquitectura en sí es defensible** porque Lab 6 hace exactamente lo mismo para multiclase. El MLP binario del proyecto es la versión natural de ese lab aplicada a clasificación binaria. La justificación debe decir: *"Aplicamos la misma arquitectura multicapa del Laboratorio 6, adaptada a clasificación binaria con una neurona de salida sigmoide."*

**Lo que no se puede defender técnicamente** sin preparación adicional son los detalles de EarlyStopping, StandardScaler y class_weight. Estos deben ser mencionados solo como *"ajustes estándar recomendados en la literatura"* o conectados a conceptos del curso (overfitting, escalado, desequilibrio de clases).

---

## 5. Riesgos en la defensa oral

Los siguientes son los puntos donde una pregunta del evaluador podría exponer conceptos no cubiertos en el curso:

| Riesgo | Pregunta probable del evaluador | Respuesta recomendada |
|---|---|---|
| **Alto** | *"¿Por qué hiciste el split por máquina y no el 80/20 del lab?"* | *"Para evitar que el modelo memorice este compresor específico. Si el split fuera aleatorio, algunas horas del mismo compresor estarían en entrenamiento y otras en prueba — el modelo aprendería ese equipo en particular, no el fenómeno general. Apliqué el concepto de varianza alta del Bias/Varianza del curso."* |
| **Alto** | *"¿Qué es class_weight='balanced' y cómo funciona?"* | *"Es un parámetro que hace que los errores en la clase minoritaria pesen más durante el entrenamiento. Su efecto práctico es el mismo que discutimos en clase: evitar que el modelo adopte la estrategia trivial de predecir siempre 'normal' para tener alta accuracy."* |
| **Alto** | *"¿Cómo cargaste los datos? Los archivos DAT no son CSV."* | *"Los datos originales están en un formato binario propietario del controlador. Desarrollé un script de conversión que los transforma en un DataFrame tabular — exactamente el tipo de datos que usamos en todos los labs. Ese paso es la etapa de preparación y limpieza de datos del pipeline."* |
| **Medio** | *"¿Qué es la impureza de Gini?"* | *"Es el criterio que scikit-learn usa por defecto para decidir qué variable y qué umbral usa el árbol en cada nodo. Elige la partición que genera subconjuntos más 'puros' — con menos mezcla de clases. No lo necesito calcular: scikit-learn lo hace automáticamente cuando llamo a `.fit()`."* |
| **Medio** | *"¿Por qué el Random Forest es mejor que el árbol de decisión para este problema?"* | *"En realidad, en este caso el árbol de decisión obtuvo un F1 ligeramente mayor. El Random Forest se incluyó como modelo adicional para ver si la agregación de múltiples árboles mejoraba la robustez — concepto del tradeoff bias/varianza. El resultado sugiere que la feature dominante es tan clara que un árbol solo ya captura casi todo."* |
| **Medio** | *"¿Qué es EarlyStopping?"* | *"Es una técnica para detener el entrenamiento automáticamente cuando el modelo deja de mejorar en los datos de validación. Evita el sobreajuste que discutimos en Clase 4: el modelo deja de aprender el patrón real y empieza a memorizar el ruido del entrenamiento."* |
| **Bajo** | *"¿Por qué usas StandardScaler para la red neuronal y no MinMaxScaler como en el curso?"* | *"Ambos escalan las variables para que el modelo no esté sesgado por las unidades. StandardScaler es la variante más común para redes neuronales porque preserva mejor la información sobre outliers. La lógica es la misma que vimos en el Lab 3."* |
| **Bajo** | *"¿La MLP dio mejores resultados que el árbol?"* | *"Sus resultados se ejecutan en Jupyter con TensorFlow. No los incluimos en el informe porque no los verificamos en el entorno de desarrollo. La arquitectura implementada sigue exactamente el esquema del Laboratorio 6."* |

---

**Conclusión del revisor:** El proyecto está sólidamente construido y los modelos nucleares (Árbol de Decisión, RF, MLP) están alineados con el contenido del curso. Los riesgos principales en la defensa son tres: la justificación de la división cross-machine, la explicación de `class_weight` y las preguntas sobre el parser DAT. Los tres tienen respuestas defendibles si se anclan en el vocabulario del curso (bias/varianza, paradoja de la exactitud, pipeline de datos). Ningún componente requiere ser eliminado del proyecto; solo requieren ser explicados con el lenguaje correcto para el nivel del curso.