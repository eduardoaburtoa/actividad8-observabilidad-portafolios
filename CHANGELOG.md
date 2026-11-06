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
