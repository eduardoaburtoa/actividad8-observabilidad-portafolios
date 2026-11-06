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
