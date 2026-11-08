## 2026-11-07 · Cierre documental de la revisión

- Ramas 01–05 fusionadas en orden mediante PR 1–5, cada una con Actions en verde: runbooks; dashboard; presupuesto de error; análisis por incidente; cierre formal.
- Rama 06: exportación única al cierre de las mejoras, con ajustes de maquetación. Tres Word/PDF revisados: 15, 13 y 10 páginas. Cobertura comprobada contra los PDF; concordancia de todos los párrafos y celdas entre Word, PDF y los tres Google Docs.
- Google Docs actualizados en sus enlaces originales y abiertos en incógnito como lector. Las copias intermedias de conversión permanecen privadas y no son los enlaces de entrega.
- Capturas de Modelo, Incidentes y Trazabilidad obtenidas del tablero con la corrida conservada; no se ejecutó `run_lab.py`.
- Mediana de detección 0.298 s frente a media 14.683 s; INC-001 acumuló 120 solicitudes lentas antes de detectarse. Son cálculos derivados de registros originales.
- Nueve pruebas y verificador sin cambios; modelo y umbral intactos. Se añade `verify_documents.py` para comprobar concordancia y páginas de cobertura.
- Rama 07 opcional descartada: el PDF de evidencia ya contiene las cuatro vistas, MLflow y cronologías; mantener una presentación duplicaría el material y dificultaría su consistencia. La decisión se documenta en un PR separado, cerrado sin fusionar.

# Historial

## 1.0.0 — 5 de noviembre de 2026

- Se conserva modelo de Actividad 6 y código de Fase II fijados a revisión, sin reentrenamiento.
- Se añade instrumentación de solicitudes, logs y spans locales, monitor SLO, PSI y control de laboratorio autenticado.
- Se ejecutan 900 solicitudes, 15 ventanas y tres incidentes recuperados. Se registran parámetros, métricas y artefactos en MLflow 2.22.2.
- Se añade Streamlit con actualización periódica, exportes verificables y tres documentos de entrega.
- La revisión detectó una credencial de prueba demasiado corta; se corrigió la prueba sin debilitar la validación de la API. Nueve pruebas pasan.
- Se corrige el cierre de alertas de calidad cuando faltan etiquetas: la ausencia de datos no implica recuperación.
- El campo histórico `server_errors` representa todas las solicitudes no exitosas del canario válido, incluidos timeouts; se documenta para evitar interpretarlo sólo como HTTP 5xx.
- Limitaciones: monitor de un proceso, canario retrospectivo repetido, ventanas por solicitudes, PSI de una variable, trazas locales. No se acredita operación productiva, SLA mensual, rentabilidad ni sustitución automática del modelo.

## 1.0.1 — Revisión de publicación

- La reproducción limpia en GitHub detectó que SQLAlchemy 2.1 elimina una clase utilizada por MLflow 2.22.2. Se fija SQLAlchemy 2.0.40, versión usada en la ejecución local. Se conserva la corrida fallida de Actions como trazabilidad.
- El registro de nuevos experimentos incluye únicamente archivos generados por esa corrida, evitando incorporar capturas antiguas. Se verifica el hash contra el manifest antes de iniciar.
- Se corrigió la transferencia truncada del Word de evidencia; se comparan todos los archivos remotos con los locales.

## Revisión 1.1.0 en ramas

### 01 — Runbooks dentro del documento técnico
- Se versiona la fuente de los tres reportes en scripts/build_reports.py. La exportación se reserva a la rama 06.
- Se incorpora tabla autónoma de disparadores, prioridades, diagnóstico, corrección, cierre y escalamiento, y explicación de seis etapas. Criterio 3.
- CI conserva las 9 pruebas y el verificador, pero deja de reejecutar el laboratorio para proteger las cifras publicadas. No se alteran modelo, umbral ni evidencia original.

## Revisión · rama 02
Dashboard documentado panel por panel, decisiones operativas y pies numerados. Capturas adicionales preparadas sin ejecutar el laboratorio; se incorporarán con los documentos en rama 06. Criterio 1.

## Revisión · rama 03
Presupuesto de error explícito en los tres reportes: permitido, consumo, saldo, burn rate y reducción de ruido. Se conserva el incumplimiento agregado de latencia. Criterio 2; exportación diferida a rama 06.

## Revisión · rama 04
Script reproducible de tiempos por incidente, media, mediana, máximo y exposición anterior a detección. JSON derivado de evidencias originales con hashes de origen; reportes explican asimetría y propuesta no implementada. Criterio 3.

## Revisión · rama 05
Referencias APA, citas autor-año, conclusiones y cobertura por criterio en las tres fuentes. Declaración de Claude actualizada según auditoría comunicada por el alumno; Gemini y Copilot conservados. Páginas se resolverán al exportar en rama 06. Criterio 4.
