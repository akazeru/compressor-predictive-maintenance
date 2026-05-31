# Matriz de Responsabilidades
## Proyecto: Mantenimiento Predictivo KAESER CSDX165

> **Formato:** adaptar al número real de integrantes del equipo.  
> Si el proyecto es **individual**, la tabla sirve como *checklist personal de redacción* — cada sección lleva una fecha límite sugerida.  
> Si el proyecto es **grupal**, asignar un responsable principal (R) y un revisor (V) por sección.

---

## Estructura del equipo

| Rol | Responsabilidad principal | Secciones del informe | Diapositivas |
|-----|--------------------------|----------------------|--------------|
| **Rol A — Dominio industrial** | Investigación del contexto técnico del compresor y los filtros. Redacción de antecedentes y definición del problema. | §2 Antecedentes industriales, §3 Definición del problema | Slides 2, 3 |
| **Rol B — Datos y pipeline** | Documentación del parser DAT, del log de eventos y de la construcción del dataset. Validación de la integridad de los datos. | §4 Fuentes de datos, §5 Ingeniería de datos | Slides 4, 5 |
| **Rol C — Features y modelos** | Documentación de las features, los modelos y las decisiones de hiperparámetros. Responsable del notebook (Commits 1–3). | §6 Ingeniería de features, §7 Metodología ML | Slides 6, 7, 8, 9 |
| **Rol D — Resultados y conclusiones** | Interpretación de métricas, visualizaciones y conclusiones. Responsable del Commit 4 y del resumen ejecutivo. | §8 Resultados, §9 Discusión, §10 Limitaciones, §11 Conclusiones, §12 Trabajo futuro | Slides 10, 11, 12, 13, 14 |

---

## Responsabilidades detalladas

### Rol A — Dominio Industrial

| Tarea | Entregable | Fecha límite |
|-------|-----------|--------------|
| Leer §8.11.4 y §5.6.2 del manual SIGMA CONTROL 2 (español) | Notas de referencia para §2 | — |
| Redactar §2.1 Compresor KAESER CSDX165 (funcionamiento, VFD, SIGMA CONTROL 2) | Borrador §2.1 | — |
| Redactar §2.2 Mecanismo del switch de ΔP (binario vs. analógico) | Borrador §2.2 | — |
| Redactar §2.3 Intervalo de mantenimiento (referencia al manual + datos observados) | Borrador §2.3 | — |
| Redactar Tabla 2.1 Especificaciones técnicas | Tabla en formato Markdown | — |
| Redactar Tabla 2.2 Códigos de evento (0011 W, 0013 W) | Tabla en formato Markdown | — |
| Redactar §3 Definición del problema (formulación ML) | Borrador §3 + Tabla 3.1 | — |
| Crear Slides 2 y 3 en PowerPoint | Diapositivas editables | — |
| Revisar §0 Resumen ejecutivo (validar precisión industrial) | Comentarios sobre borrador | — |

**Inputs necesarios:**
- Manual *Sigma Control 2 Screw Fluid ≥ 4.1.X* (disponible en `reference/`)
- Resultados de la auditoría de eventos (`_parse_events.py`, `_alt_target_audit.py`)

---

### Rol B — Datos y Pipeline

| Tarea | Entregable | Fecha límite |
|-------|-----------|--------------|
| Documentar el formato binario DAT (Tabla 4.1 y §4.1) | Borrador §4.1 | — |
| Documentar `CompressorMsgs.txt` y el artefacto de doble despeje (§4.2) | Borrador §4.2 | — |
| Redactar §4.3 Auditoría de solapamiento temporal | Borrador §4.3 + Tabla 4.1 | — |
| Redactar Tabla 4.2 Canales DAT seleccionados | Tabla en formato Markdown | — |
| Redactar §5 Ingeniería de datos (pipeline completo, las 4 funciones principales) | Borrador §5 + Tabla 5.1 | — |
| Crear Fig 2 como figura de apoyo narrativo en §5 | Verificar que `fig2_episode_timeline.png` es legible en el formato del informe | — |
| Crear Slides 4 y 5 en PowerPoint | Diapositivas editables | — |
| Revisar las celdas 12–21 del notebook (Commit 2) y documentar los parámetros clave | Comentarios en el notebook | — |

**Inputs necesarios:**
- Scripts de auditoría: `_bf_audit.py`, `_temporal_audit.py`
- Código del notebook: celdas 6–7 (funciones DAT), celdas 8–10 (funciones de eventos), celdas 13–20 (extracción y ensamblado)
- Figura generada: `figures/fig2_episode_timeline.png`

---

### Rol C — Features y Modelos

| Tarea | Entregable | Fecha límite |
|-------|-----------|--------------|
| Redactar §6.1 Feature set MVP (descripción de las 8 features + hipótesis física) | Borrador §6.1 + Tabla 6.1 | — |
| Redactar §6.2 El feature de acumulación `hours_loaded_since_clear` | Borrador §6.2 | — |
| Redactar §7.1 Estrategia de división train/test (cross-machine temporal) | Borrador §7.1 | — |
| Redactar §7.2 Manejo del desequilibrio de clases | Borrador §7.2 | — |
| Redactar §7.3–7.5 Descripción de los tres modelos (DT, RF, MLP) | Borrador §7.3–7.5 + Tabla 7.1 | — |
| Redactar §7.6 Métricas de evaluación (Recall como primaria, F1 secundaria) | Borrador §7.6 | — |
| Insertar Fig 3 (árbol de decisión) y Fig 4 (feature importance) en el informe | Figuras con pie de foto | — |
| Crear Slides 6, 7, 8, 9 y 10 en PowerPoint | Diapositivas editables | — |
| Asegurar reproducibilidad del notebook (kernel restart → run all sin errores) | Notebook ejecutable | — |

**Inputs necesarios:**
- Código del notebook: celdas 22–27 (Commit 3 — modelos)
- Figuras: `figures/fig3_decision_tree.png`, `figures/fig4_feature_importance.png`
- Resultados numéricos del `_verify_commit3.py`

---

### Rol D — Resultados y Conclusiones

| Tarea | Entregable | Fecha límite |
|-------|-----------|--------------|
| Redactar §8.1 Tabla de métricas comparativa (incluyendo MLP si disponible) | Borrador §8.1 + Tablas 8.1 y 8.2 | — |
| Redactar §8.2 Matrices de confusión con interpretación operacional | Borrador §8.2 | — |
| Redactar §8.3 Importancia de features (resultados cuantitativos) | Borrador §8.3 | — |
| Redactar §9 Discusión (5 puntos: hipótesis, Recall, Precision, cross-machine, DT vs RF) | Borrador §9 completo | — |
| Redactar Tabla 10.1 Limitaciones | Tabla completa en Markdown | — |
| Redactar §11 Conclusiones (respuesta directa a la pregunta de investigación) | Borrador §11 | — |
| Redactar §12 Trabajo futuro | Borrador §12 | — |
| Redactar §0 Resumen ejecutivo (última tarea, cuando todo lo demás esté finalizado) | Borrador §0 (400–500 palabras) | — |
| Insertar Fig 5 y Fig 6 en §8 del informe | Figuras con pie de foto | — |
| Crear Slides 11, 12, 13 y 14 en PowerPoint | Diapositivas editables | — |
| Ensamblar el informe completo (integrar borradores de todos los roles) | Documento Word/LaTeX final | — |
| Revisar consistencia del informe (terminología, números, referencias cruzadas) | Documento revisado | — |

**Inputs necesarios:**
- Figuras: `figures/fig5_confusion_matrices.png`, `figures/fig6_model_comparison.png`
- Resultados del `_verify_commit3.py` y del `_verify_commit4.py`
- Código del notebook: celdas 28–35 (Commit 4 — visualizaciones)

---

## Dependencias entre roles

```
Rol A (Industrial)  ────────────────────────────→  §2, §3
                                                         ↓
Rol B (Pipeline)    →  §4, §5  →  [Dataset listo]  →  Rol C
                                                         ↓
Rol C (Modelos)     →  §6, §7  →  [Modelos + métricas]  →  Rol D
                                                                ↓
Rol D (Resultados)  →  §8–§12 → [§0 Resumen ejecutivo]
```

**Orden de redacción recomendado:**
1. §4 y §5 (Rol B) — sin esto no hay §6 ni §7
2. §2 y §3 (Rol A) — puede hacerse en paralelo con Rol B
3. §6 y §7 (Rol C) — requiere §4 y §5 finalizados
4. §8, §9, §10, §11, §12 (Rol D) — requiere §6 y §7 finalizados
5. §0 Resumen ejecutivo (Rol D) — última sección en redactarse

---

## Checklist de entrega

### Informe

- [ ] Portada completa (título, autor, institución, fecha)
- [ ] Resumen ejecutivo ≤ 500 palabras
- [ ] Todas las tablas tienen número y título
- [ ] Todas las figuras tienen número, título y fuente (`figures/figN_*.png`)
- [ ] Referencias completas (manual KAESER + librerías + papers)
- [ ] Anexo E: notebook adjunto (`.ipynb`)
- [ ] Extensión total: 25–35 páginas sin anexos
- [ ] Ortografía y gramática revisadas
- [ ] Números consistentes entre texto y tablas (Recall 85,X % en todos los lugares donde aparece)

### Presentación

- [ ] 14 diapositivas (±1)
- [ ] Duración ensayada: 15–20 min
- [ ] Figuras importadas en alta resolución (no pantallazos)
- [ ] Slides B1–B4 preparadas como respaldo para preguntas
- [ ] Paleta de colores consistente con las figuras del notebook
- [ ] Fuente mínima 20 pt en todo el contenido

### Notebook

- [ ] Kernel restart → run all sin errores
- [ ] 36 celdas ejecutadas con outputs visibles
- [ ] `figures/` con las 6 figuras generadas
- [ ] Todas las variables clave tienen docstring
- [ ] `RANDOM_STATE = 42` en todas las llamadas estocásticas

---

## Reparto alternativo para proyecto individual

Si el proyecto es de un solo autor, usar esta secuencia de redacción:

| Semana | Secciones | Días estimados |
|--------|-----------|----------------|
| S1 | §4 Fuentes de datos + §5 Ingeniería de datos | 3 días |
| S1 | §2 Antecedentes + §3 Definición del problema | 2 días |
| S2 | §6 Features + §7 Metodología ML | 3 días |
| S2 | §8 Resultados + §9 Discusión | 2 días |
| S3 | §10 Limitaciones + §11 Conclusiones + §12 Trabajo futuro | 1 día |
| S3 | §0 Resumen ejecutivo | 1 día |
| S3 | Integración, revisión y presentación PPT | 2 días |
