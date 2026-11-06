# Runbooks de respuesta

Los procedimientos están implementados en `scripts/run_lab.py`; el registro real está en `evidencias/runbook_steps.json`. El laboratorio inyecta fallas sólo en loopback, con token temporal y `LAB_MODE=1`. En producción, deshabilitar y excluir el control de inyección; no abrir el puerto de laboratorio.

## Preparación común

Responsable de respuesta: operador MLOps; decisión de uso del resultado: banquero; cambio de modelo/datos: propietario del modelo con validación humana. Antes de la prueba, verificar hash y `/health`, guardar versión de configuración y generar referencia de 60 textos. No hay clientes reales. Los roles son una propuesta de gobierno; la ejecución documentada es automatizada localmente.

## RB01 Latencia y disponibilidad

Disparador: burn rate >2 durante dos ventanas consecutivas de 60 solicitudes. Disponibilidad P1; latencia P2. Confirmar alcance con estados HTTP, p95, trace_id y revisión de servicio. En el laboratorio revertir `mode=normal`; comprobar que el hash no cambió. Exigir dos ventanas sanas antes de cerrar. Registrar detección, corrección y resolución. Si persiste tras dos ventanas posteriores a la corrección, mantener abierto, detener uso de la salida y escalar al operador; no realizar reintentos ilimitados. Esta última escalada humana es un procedimiento, no un servicio de guardia implementado.

## RB02 Calidad

Disparador: recall <0.75 o F1 <0.65, con ≥15 etiquetas negativas y ≥60 solicitudes, durante dos ventanas. Prioridad P2. Confirmar etiquetas, umbral 0.20 y versión. Revertir la inversión de probabilidad simulada mediante `mode=normal`; no modificar pesos. Verificar dos ventanas recuperadas con etiquetas suficientes. Si faltan etiquetas, mantener el incidente abierto y solicitar etiquetado, sin presumir recuperación. Si no mejora, retirar resultados de uso y solicitar evaluación del modelo con aprobación humana.

## RB03 Drift de longitud

Disparador: PSI >0.20 en dos ventanas. Prioridad P3 de investigación. Revisar bins, muestra y origen; poner en cuarentena el lote sintético de textos repetidos ocho veces. Restituir la entrada de referencia y registrar ticket local de revisión. Cerrar tras dos ventanas con PSI normal. La cuarentena aquí cambia el generador del laboratorio; una cola de producción necesitaría almacenamiento y control de acceso. No confundir drift con degradación ni reentrenar sin diagnóstico.

## Cierre y aprendizaje

Cada caso deja las etapas prepare, detect, diagnose, correct, verify y postmortem. MTTD = detección − inyección; MTTR = resolución − detección. El presupuesto consumido no se reinicia al cerrar una alerta. Registrar causa, acción reversible, evidencia de recuperación y tarea preventiva. La deduplicación es por regla activa y exige persistencia; no silencia un P1 por tener P2 activo. Se mantienen escalamiento y sustitución de modelo como decisiones humanas, no publicaciones externas automáticas.
