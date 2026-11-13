<p align="center"><img src="documentos/vertice_logo.png" width="130" alt="Vértice AI"></p>
<h1 align="center">Actividad 8 · Observabilidad y continuidad</h1>
<p align="center">Eduardo Aburto Angulo · Gestión de proyectos de inteligencia artificial<br>Módulo 3 · Semana 10 · Temas 19 y 20</p>

## Guía de entregables y resultados

Implementé un laboratorio que detecta y recupera incidentes del servicio de clasificación de noticias de Fase II. La evidencia procede de **900 solicitudes HTTP reales**, 15 ventanas y **3 incidentes simulados recuperados**. Las fallas son controladas; no corresponden a tráfico bancario de producción.

| Quiero revisar | Abrir |
|---|---|
| Documento técnico y decisiones | [Leer en GitHub →](documentos/01-documento-tecnico/README.md) |
| Evidencia de implementación y MLflow | [Leer en GitHub →](documentos/02-evidencia-implementacion/README.md) · [Exportación real MLflow](evidencias/mlflow_export.json) |
| Incidentes y ejecución de runbooks | [Leer en GitHub →](documentos/03-simulacion-incidentes/README.md) · [Pasos registrados](evidencias/runbook_steps.json) |
| Tablero Streamlit | [Aplicación](app.py) · instrucciones debajo |
| Alertas y procedimientos | [Configuración](config/alertas.json) · [Runbooks](runbooks/README.md) |
| Validar los resultados | [Verificador](scripts/verify_evidence.py) · [Resultados originales](evidencias/summary.json) |

![Detección y recuperación](evidencias/dashboard_mediciones.png)

[**Explorar toda la documentación →**](documentos/README.md)

<details>
<summary>Edición en Google Docs y descargas académicas</summary>


[Documento técnico](https://docs.google.com/document/d/1-DStylkW7mW17Qdpj9g-uxETDyGbEEtasdzIzSjp1Mg/edit) · [Evidencia de implementación](https://docs.google.com/document/d/1kfE5N71RCpxyjlwEpxE_tJGuRY7CpFboSdRzApfX6qU/edit) · [Simulación de incidentes](https://docs.google.com/document/d/1EKSEgWnlxt1bbbTSyjD0Cb_J-xvNY3GnGHlA1ACmJwM/edit). Documentos actualizados en sus enlaces originales: editables por el autor y con lectura pública comprobada en incógnito el 7 de noviembre de 2026. Los PDF y Word del repositorio contienen el mismo texto; la tabla de cobertura remite a la paginación PDF/Word verificada.

[PDF y Word descargables](documentos/README.md). Los README son ahora la ruta principal de lectura y navegación.

</details>

## Resultado que conviene interpretar

- **Disponibilidad: 900/900 solicitudes exitosas.** Presupuesto permitido: 9 fallas; consumido: 0.
- **Latencia: 120/900 solicitudes lentas.** Presupuesto permitido: 9; consumido: 120. El SLO agregado de 99 % **no se cumplió**, aunque terminó recuperado.
- **Tres alertas emitidas frente a seis avisos por ventanas con incumplimiento:** 50 % menos notificaciones respecto de avisar cada ventana. Esto no mide una tasa de falsos positivos.
- Detección mediana: **0.298 s**, media: **14.683 s** y máximo: **43.457 s**. La mediana describe mejor el caso típico de estos tres ensayos; la media revela la exposición prolongada. [Cálculo por incidente](evidencias/incident_analysis.json): **120 solicitudes lentas antes de detectar INC-001**; recuperación media desde detección hasta dos ventanas sanas: **0.273 s**. Son tres incidentes locales y secuenciales, no compromisos de producción.
- Calidad del canario normal: precisión 0.9048, recall 0.9500 y F1 0.9268. Son 60 textos históricos repetidos; no una evaluación independiente ni una promesa de rendimiento financiero.

## Cobertura de la rúbrica

| Criterio de 25 puntos | Implementación verificable |
|---|---|
| Métricas, logs y trazas | [Instrumentación](observabilidad/service.py), [métricas](observabilidad/monitor.py), [logs](evidencias/logs.jsonl), [spans](evidencias/traces.jsonl) correlacionados por trace_id |
| Alertas SLO y error budgets | 99 %, ≤250 ms, burn rate >2, dos ventanas, prioridades P1–P3 y deduplicación; [eventos](evidencias/alerts.json) |
| Simulación y respuesta | Latencia, degradación de salida y drift de longitud; [incidentes](evidencias/incidents.json) y ejecución de runbooks |
| Documentación y automatización | Tres reportes, rollback de configuración, cuarentena y escalamiento local; no reentrenamiento ni operaciones financieras automáticas |

## Revisión final y validación sin alterar la evidencia

Los seis apartados exigidos tienen sección propia en el informe técnico (antes: cinco). Hay **2 figuras numeradas** en el documento técnico, **7** en evidencias y **0** en simulación, que presenta tablas. Los tres reportes incluyen referencias, conclusiones y cobertura por página. [Comparación antes/después](evidencias/document_revision_comparison.json) · [Concordancia Word/PDF/Google Docs](evidencias/document_export_validation.json).

```bash
python -m pip install -r requirements.txt
python -m pip install pypdf==6.1.1
python -m pytest pruebas -q
python scripts/verify_evidence.py
python scripts/analyze_incidents.py
python scripts/verify_documents.py
```

Estos comandos no ejecutan el laboratorio. El análisis derivado conserva las cifras originales y sus hashes. Las nueve pruebas y el verificador no fueron modificados. El modelo y el umbral 0.20 permanecen intactos.

| Mejora | Revisión |
|---|---|
| Runbooks autónomos en el informe | [PR 1](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/pull/1) |
| Tablero panel por panel | [PR 2](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/pull/2) |
| Presupuesto de error explícito | [PR 3](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/pull/3) |
| Detección y recuperación por incidente | [PR 4](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/pull/4) |
| Referencias, conclusiones y cobertura | [PR 5](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/pull/5) |
| Exportación final y concordancia de formatos | Rama `mejora/06-exportacion-final` |

## Reproducir desde cero (nueva corrida)

**Esta sección genera nuevas mediciones y sobrescribe la evidencia de la copia de trabajo.** Para auditar la entrega publicada, usa únicamente la sección anterior. Ejecuta una nueva corrida en otro clon si quieres conservar intactos los archivos originales.

Python 3.12 y SQLAlchemy 2.0.40 fijado por compatibilidad con MLflow 2.22.2. Ejecutar desde la raíz del repositorio. La instalación descarga paquetes; el laboratorio usa el modelo y dataset versionados, sin servicios de pago ni claves externas.

```bash
git clone https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios.git
cd actividad8-observabilidad-portafolios
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest pruebas -q
python scripts/verify_evidence.py
python scripts/run_lab.py
python scripts/verify_evidence.py
python scripts/figures.py
```

El laboratorio tarda aproximadamente un minuto, inicia una API en un puerto local libre y la detiene al terminar. Genera claves aleatorias temporales y conserva cada sesión en `runtime/`. Actualiza las evidencias: guarda una copia si deseas conservar la corrida publicada. No ejecutar dos laboratorios simultáneos en la misma carpeta. Una máquina lenta puede afectar la latencia y generar alertas adicionales; eso es una medición real, no un motivo para modificar resultados a mano.

## Abrir Streamlit y MLflow

```bash
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8518
```

Abre http://127.0.0.1:8518. El tablero refresca cada tres segundos. Para observar cambios, ejecuta `run_lab.py` en otra terminal. Sin laboratorio activo presenta la última corrida guardada. En Streamlit Community Cloud se puede seleccionar `app.py` para visualizar la evidencia publicada; ese despliegue no ejecuta incidentes por sí mismo.

Después de ejecutar el laboratorio:

```bash
python -m mlflow ui --backend-store-uri sqlite:///runtime/mlflow.db --host 127.0.0.1 --port 5088
```

Abre http://127.0.0.1:5088 y el experimento `Actividad8_observabilidad_portafolios`. Verás parámetros, métricas por paso y artefactos. El identificador de la corrida publicada es `c0a8fa3f79b84eb4bec63d70b674bf32`; cada reproducción obtiene uno nuevo. La base SQLite local no se publica: [exportación portable](evidencias/mlflow_export.json) y archivos JSONL permiten revisar resultados sin MLflow.

## Arquitectura y límites

Cliente canario → API FastAPI instrumentada → SVM calibrada congelada → logs y spans JSONL → monitor SLO y drift → alertas y runbooks → MLflow y Streamlit.

Las trazas contienen spans padre e hijo locales, no una instalación de OpenTelemetry Collector ni propagación distribuida. Las métricas de calidad necesitan etiquetas; sin ellas, una alerta existente no se da por resuelta. El PSI sólo examina longitud textual y no demuestra concept drift. Las ventanas son de solicitudes, no un SLO mensual.

Se conserva el modelo de [Actividad 6](https://github.com/eduardoaburtoa/actividad6-evaluacion-portafolios) servido en [Fase II](https://github.com/eduardoaburtoa/fase2-despliegue-portafolios), revisión `b6ecb7a0e6b01ece989369b7b67178fe7d7cc2a4`. Su hash está en [manifest](modelos/manifest.json), umbral 0.20 y lengua inglés. Un rollback aquí restaura la configuración de servicio; no sustituye pesos ni reentrena.

## Contexto bancario como anexo

Mi propósito es preparar revisiones de portafolio con señales trazables y revisión del banquero. Los [150 clientes ficticios](contexto/) se conservan como continuidad didáctica; no alimentan el monitor ni son datos personales reales. La comisión de 1 % por compra y 1 % por venta es un supuesto académico, no una tarifa verificada de BBVA. El clasificador no estima rendimientos, no recomienda cambiar fondos y no ejecuta operaciones. El foco evaluado de esta entrega es la confiabilidad operativa.

## Organización

`observabilidad/`: instrumentación y monitor · `config/`: reglas · `scripts/`: laboratorio, gráficas y verificación · `evidencias/`: mediciones reales exportadas · `runbooks/`: respuesta · `pruebas/`: pruebas automatizadas · `documentos/`: índice y tres README de lectura, con descargas académicas · `backend/`, `modelos/`, `datos/`, `frontend/` y `contexto/`: continuidad de Fase II.

[Validación automática](https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios/actions) · [Historial y decisiones](CHANGELOG.md) · [Aviso de uso académico](AVISO.md)
