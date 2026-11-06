from pathlib import Path
import json,copy
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1]; E=R/'evidencias'; O=R/'documentos';s=json.loads((E/'summary.json').read_text());w=json.loads((E/'windows.json').read_text())
T=R/'documentos/Documento_tecnico.docx'
def text_in(el,value):
 ts=el.findall('.//'+qn('w:t'))
 if ts:
  ts[0].text=value
  for t in ts[1:]:t.text=''
def base(subtitle):
 d=Document(T);body=d.element.body
 text_in(body[4],'ACTIVIDAD 8');text_in(body[6],subtitle)
 d.tables[0].cell(1,1).text='Actividad 8 · Módulo 3 / Semana 10 · Temas 19 y 20'
 d.tables[0].cell(5,1).text='5 de noviembre de 2026'
 d.tables[1].cell(1,2).text='ChatGPT/Codex: apoyo en programación, ejecución de pruebas, simulaciones locales, documentación y revisión visual. Las mediciones proceden de ejecuciones reales con fallas inyectadas.'
 for row in d.tables[1].rows[2:]:row.cells[1].text='Antecedentes';row.cells[2].text='Herramienta mencionada en actividades previas; no se atribuye ejecución nueva en Actividad 8.'
 for el in list(body)[25:]:
  if el.tag!=qn('w:sectPr'):body.remove(el)
 d.core_properties.title=subtitle;d.core_properties.author='Eduardo Aburto Angulo'
 return d

def h(d,t):d.add_heading(t,level=1)
def p(d,t):d.add_paragraph(t)
def page(d):d.add_page_break()
def table(d,heads,rows):
 t=d.add_table(rows=1,cols=len(heads));t.autofit=False
 for c,v in zip(t.rows[0].cells,heads):c.text=str(v)
 for row in rows:
  for c,v in zip(t.add_row().cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  for c in row.cells:
   pr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'004481' if ri==0 else ('EAF3FA' if ri%2 else 'FFFFFF'));pr.append(sh)
   borders=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
   pr.append(borders)
   for pa in c.paragraphs:
    pa.paragraph_format.space_after=Pt(5);pa.paragraph_format.space_before=Pt(5)
    for run in pa.runs:run.font.size=Pt(9);run.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '072146')
  trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
 d.add_paragraph()
def image(d,name,width=6):d.add_picture(str(E/name),width=Inches(width))
def save(d,name):d.save(O/(name+'.docx'))

d=base('Monitorización y gobernanza del servicio de portafolios')
h(d,'Propósito y decisión operativa')
p(d,'Como banquero Sr., necesito saber cuándo una señal deja de ser confiable antes de incorporarla a una revisión de portafolio. En esta entrega implementé observabilidad para la API de clasificación de noticias de Fase II. Mi decisión es mantener la solución como laboratorio académico: las tres fallas simuladas se detectaron y recuperaron, pero la corrida completa incumplió el presupuesto de latencia. La recuperación no equivale a acreditar producción.')
p(d,'El objetivo verificable fue instrumentar métricas, logs y trazas; detectar tres incidentes mediante reglas persistentes; ejecutar respuestas reversibles y conservar evidencia en MLflow. Ejecuté 900 solicitudes HTTP en 15 ventanas de 60 observaciones. No usé datos de clientes reales ni ejecuté movimientos de inversión.')
h(d,'Continuidad y alcance')
p(d,'Conservé la SVM calibrada y el umbral 0.20 de Actividad 6. La clase positiva significa noticia negativa y el idioma soportado es inglés. Fase II aporta la API FastAPI. La referencia de código es b6ecb7a0e6b01ece989369b7b67178fe7d7cc2a4; el manifest del modelo permite comprobar sus bytes. Esta actividad evalúa la operación del servicio y no vuelve a seleccionar modelos con el test.')
p(d,'Utilicé 60 textos del test retrospectivo: 20 negativos y 40 no negativos, seleccionados con semilla 42. Repito esa muestra en cada ventana para aislar el efecto de las fallas. Las etiquetas son conocidas y la distribución no representa la cartera ni tráfico real. Las métricas del canario no sustituyen las del test completo de 452 registros.')
h(d,'Arquitectura implementada')
p(d,'El cliente envía solicitudes a la API local instrumentada. El middleware registra estado, duración, versión y trace_id sin guardar noticias ni claves. El monitor agrega ventanas, calcula SLI y PSI y dispara acciones locales. MLflow registra parámetros, métricas por paso y artefactos; Streamlit actualiza la vista cada tres segundos. Los spans padre e hijo son locales en JSONL; no implementé un Collector de OpenTelemetry ni propagación entre servicios.')
page(d);h(d,'Indicadores y contratos de medición')
table(d,['Indicador','Definición y uso'],[
['Disponibilidad','Respuestas HTTP 200 / solicitudes válidas del canario. Timeouts y respuestas no exitosas consumen presupuesto.'],
['Latencia','Tiempo cliente de ida y vuelta; p95 por ventana. SLI: proporción de solicitudes exitosas con duración ≤250 ms.'],
['Tráfico y recursos','Solicitudes / segundo; memoria RSS y CPU del proceso. 512 MB es presupuesto de planificación, no límite impuesto.'],
['Calidad','Precisión, recall y F1 de noticia negativa, sólo sobre respuestas exitosas con etiqueta. Mínimo 15 negativos por ventana.'],
['Drift','PSI de longitud en palabras frente al canario inicial; bins 0,10,20,30,50,1000000 y suavizado +0.5.'],
['Logs y trazas','Timestamp, ruta, método, estado, duración, modo y revisión. trace_id une solicitud, log y spans con padre, inicio y fin.']])
p(d,'El campo exportado server_errors conserva su nombre histórico, pero cuenta cualquier respuesta no exitosa del canario, no sólo errores 5xx. El control de laboratorio exige una clave distinta de la API y LAB_MODE=1. El proceso escucha sólo en loopback. Las pruebas comprueban que texto y claves no se filtran al log.')
h(d,'SLO y presupuesto de error')
p(d,'Definí SLO de disponibilidad de 99 % y SLO de latencia de 99 % de solicitudes ≤250 ms. Para N solicitudes, presupuesto permitido = N × (1 − SLO); consumo = número de solicitudes malas; saldo = permitido − consumo. Burn rate = fracción mala / (1 − SLO). Son ventanas por solicitudes del laboratorio, no ventanas mensuales de producción ni un SLA contractual.')
p(d,'En 900 solicitudes, cada presupuesto permite 9 eventos. La disponibilidad consumió cero. La latencia consumió 120: saldo −111 y cumplimiento agregado 86.67 %. El burn agregado fue 13.33 veces la tasa permitida. El servicio volvió a su condición normal después de la intervención, pero ese consumo permanece registrado.')
page(d);h(d,'Alertas y reducción de ruido')
table(d,['Regla','Disparador y prioridad','Respuesta'],[
['Disponibilidad','Burn >2 en dos ventanas de 60; P1','Diagnóstico y rollback de configuración; escalamiento si persiste'],
['Latencia','Burn >2 en dos ventanas de 60; P2','Restaurar modo normal y verificar dos ventanas'],
['Calidad','Recall <0.75 o F1 <0.65 con etiquetas suficientes; P2','Revertir salida alterada y revisar calidad'],
['Drift','PSI >0.20 durante dos ventanas; P3','Cuarentena del lote sintético y revisión local']])
p(d,'La persistencia evita avisar por un único incumplimiento. La deduplicación emite una sola apertura por regla activa; exige dos ventanas sanas para cerrar. Si faltan etiquetas, una alerta de calidad permanece abierta. Un P1 no queda silenciado por un P2. El mínimo de 60 solicitudes evita interpretar lotes incompletos. Los umbrales son decisiones de laboratorio y requieren recalibración con historia operativa.')
p(d,'El motor observó seis ventanas que habrían generado aviso individual y emitió tres aperturas: reducción del 50 % frente a esa política simple. No infiero una tasa de falsos positivos ni una validación estadística con tres incidentes. En producción incorporaría ventanas temporales cortas y largas y guardias; aquí la persistencia usa dos ventanas consecutivas de solicitudes.')
h(d,'Data drift y límites del diagnóstico')
p(d,'Calculo PSI = suma de (q − p) × ln(q/p), usando proporciones suavizadas. El experimento repite ocho veces cada texto para desplazar la longitud. La alerta indica cambio de entrada, no prueba pérdida de capacidad predictiva. No cubre cambios semánticos de igual longitud, idioma, etiquetas ni concept drift. Para producción añadiría seguimiento de embeddings y calidad con etiquetas retrasadas, por segmentos y con tamaño muestral suficiente.')
h(d,'Dashboard para decidir')
p(d,'La vista Servicio presenta disponibilidad, p95, burn rate, presupuesto, tráfico y memoria. Modelo muestra precisión, recall, F1 y PSI. Incidentes permite examinar aperturas, cierres y pasos del runbook. Trazabilidad expone resumen, corrida MLflow y spans. Cuando el laboratorio está detenido, el tablero indica que muestra la última corrida; no presenta esos datos como tráfico vivo.')
page(d);h(d,'Runbooks de respuesta a incidentes')
table(d,['Regla y disparador','Diagnóstico y corrección','Cierre y escalamiento'],[
['RB01 · P2 latencia / P1 disponibilidad. Burn >2 en dos ventanas consecutivas de 60 solicitudes.', 'Confirmar estado HTTP, p95, modo, revisión y hash; correlacionar trace_id. Restaurar mode=normal sin cambiar el modelo.', 'Cerrar tras dos ventanas sanas. Si persiste después de la corrección, mantener abierto, detener uso de la salida y escalar al operador.'],
['RB02 · P2. Recall <0.75 o F1 <0.65 en dos ventanas de 60, con ≥15 negativos etiquetados por ventana.', 'Comprobar etiquetas, versión y umbral 0.20. Revertir la inversión de probabilidad simulada con mode=normal.', 'Dos ventanas recuperadas con etiquetas suficientes. Sin etiquetas no cerrar; solicitar etiquetado. Si persiste, retirar resultados y escalar al responsable del modelo.'],
['RB03 · P3. PSI de longitud >0.20 durante dos ventanas de 60 solicitudes.', 'Revisar bins, muestra y origen. Poner en cuarentena el lote sintético y restablecer la entrada de referencia.', 'Dos ventanas con PSI normal. Si no se recupera, conservar cuarentena y ticket local de revisión; no reentrenar automáticamente.']])
p(d,'El ciclo registrado contiene seis etapas: prepare verifica alcance, referencia y versión; detect identifica la regla; diagnose confirma la causa; correct ejecuta una acción reversible; verify contrasta dos ventanas sanas; postmortem documenta causa y prevención. Exijo dos ventanas sanas para evitar cerrar por una recuperación aislada. Con etiquetas insuficientes, la calidad permanece sin confirmar. La versión extensa se conserva en runbooks/README.md; este apartado contiene las decisiones necesarias para interpretar la respuesta por sí solo.')
page(d);h(d,'Respuesta automatizada y gobernanza')
p(d,'Los runbooks completos están en runbooks/README.md. Cada ejecución registra preparación, detección, diagnóstico, corrección, verificación y postmortem. RB01 restaura la configuración ante latencia; RB02 revierte la alteración simulada de probabilidades; RB03 aparta el lote de entrada alterado y registra escalamiento local. El rollback no cambia el artefacto del modelo. El reentrenamiento requiere diagnóstico, evaluación y autorización humana y no se ejecutó.')
p(d,'Si la corrección no recupera dos ventanas, el procedimiento mantiene el incidente abierto y escala al operador; no establece reintentos indefinidos. Los roles propuestos son operador MLOps para continuidad, propietario del modelo para validación y banquero para uso de señales. El ticket de escalamiento es un registro local, no un envío a un servicio externo de guardia.')
table(d,['Incidente','Detección s','Recuperación s','Estado'],[[i['type'],f"{i['detection_seconds']:.3f}",f"{i['recovery_seconds']:.3f}",i['status']] for i in s['incidents']])
p(d,'MTTD se mide desde inyección a detección y MTTR desde detección hasta cierre verificado. Las medias fueron 14.683 s y 0.273 s. La latencia tarda más en detectarse porque 120 solicitudes secuenciales acumulan el retraso inyectado de 350 ms; las otras fases corren rápidamente en el mismo host. Estos tiempos no son expectativas de recuperación para una operación distribuida.')
h(d,'Mantenimiento y deuda técnica')
p(d,'Versioné configuración y scripts, conservé hash de modelo, evidencia portable y pruebas de controles. MLflow usa SQLite local; cada reproducción obtiene una corrida distinta. La promoción productiva requeriría almacenamiento central de telemetría, autenticación y permisos por rol, retención, alertamiento a guardia, control transaccional de acciones y pruebas de carga. El laboratorio no debe exponerse como endpoint público.')
p(d,'Propongo revisar SLO y umbrales mensualmente con el propietario del servicio; ensayar runbooks tras cambios de modelo; conservar incidentes y decisiones en un registro auditado. La propuesta de retención es 30 días de telemetría operativa y 90 de incidentes, sujeta a política institucional. No se ha implementado borrado automático ni aprobación regulatoria.')
page(d);h(d,'Evidencia y conclusión')
p(d,'Entrego scripts ejecutables, nueve pruebas automatizadas, un verificador que recalcula métricas y correlaciona trazas, tres documentos y un tablero Streamlit. MLflow registró la corrida '+s['mlflow_run_id']+' con estado FINISHED. Las capturas y exportaciones se presentan en Evidencia de implementación; las cronologías en Simulación de incidentes.')
p(d,'Mi conclusión es que el prototipo permite detectar y atender las fallas ensayadas de forma trazable. Conservo explícitamente el incumplimiento agregado de latencia y los límites de la muestra. Mi criterio como banquero es detener el uso de una señal dudosa y solicitar revisión, antes de convertir un resultado técnico en una acción sobre el patrimonio de un cliente.')
h(d,'Contexto de negocio complementario')
p(d,'La continuidad del proyecto conserva 150 personajes ficticios con posiciones de 5 a 20 millones de pesos. Su función es didáctica: dar personalidad a escenarios sin usar datos reales. La comisión de 1 % por compra y 1 % por venta es un supuesto académico; no constituye una tarifa verificada de BBVA. Las comisiones de fondos dependen de documentación y series vigentes. No uso esos supuestos para medir éxito del monitor ni para recomendar cambios de fondos.')
h(d,'Fuentes y trazabilidad')
for t in ['Universidad Tecmilenio. Rúbrica Actividad 8 y temas 19 y 20, materiales proporcionados por el alumno. Temas 17 y 18 como continuidad de MLOps y despliegue.','MLflow. Tracking y Tracking API. https://mlflow.org/docs/latest/tracking/ y https://mlflow.org/docs/latest/tracking/tracking-api','Google SRE Workbook. Alerting on SLOs. https://sre.google/workbook/alerting-on-slos/','OpenTelemetry. Signals y Traces. https://opentelemetry.io/docs/concepts/signals/ y https://opentelemetry.io/docs/concepts/signals/traces/','Repositorio de entrega: https://github.com/eduardoaburtoa/actividad8-observabilidad-portafolios. Código de origen y manifest preservados; consulta técnica el 5 de noviembre de 2026.']:p(d,t)
save(d,'Documento_tecnico')

d=base('Evidencia de implementación de observabilidad')
h(d,'Qué demuestra esta evidencia')
p(d,'Presento mediciones de una ejecución local del servicio instrumentado. Se enviaron 900 solicitudes HTTP reales a la API y se inyectaron tres fallas controladas. La sesión '+s['session']+' usa UTC; corresponde al 5 de noviembre de 2026 en Ciudad de México. No es una captura de producción bancaria.')
p(d,'La figura muestra los cambios de latencia, recall y longitud por ventana. Las franjas amarillas identifican las ventanas con falla. Las mediciones posteriores documentan recuperación; la última ventana termina sin alertas activas.')
image(d,'dashboard_mediciones.png',5.8)
page(d);h(d,'Presupuesto y política de notificación')
image(d,'presupuesto_alertas.png',6)
p(d,'El SLO agregado de latencia no se cumple: 120 solicitudes consumidas frente a 9 permitidas. La disponibilidad sí conserva su presupuesto. La política de persistencia reduce de seis avisos por ventana a tres aperturas; no convierte el incidente en un éxito de SLO ni acredita ausencia de falsos positivos.')
h(d,'Registro real en MLflow')
p(d,'Experimento: Actividad8_observabilidad_portafolios. Run ID: '+s['mlflow_run_id']+'. Estado leído con MlflowClient.get_run: FINISHED. Se registraron configuración de SLO, semilla, hash, referencia de código y 15 pasos de métricas. Los artefactos incluyen solicitudes, ventanas, incidentes, logs y spans. El archivo mlflow_export.json es una exportación del servicio local, no una tabla escrita manualmente.')
table(d,['Evidencia','Ubicación relativa'],[['Parámetros y estado','evidencias/mlflow_export.json'],['Mediciones por ventana','evidencias/windows.json'],['Solicitudes y trace_id','evidencias/requests.jsonl'],['Aperturas y cierres','evidencias/alerts.json'],['Pasos ejecutados','evidencias/runbook_steps.json'],['Pruebas automatizadas','evidencias/pytest.xml']])
page(d);h(d,'Verificación y reproducción')
p(d,'El verificador recalcula los indicadores desde requests.jsonl, reconstruye aperturas y cierres, comprueba el hash del modelo, los spans padre e hijo y las cronologías. Nueve pruebas verifican presupuesto, persistencia, muestras mínimas, drift, controles y privacidad. La evidencia se puede inspeccionar sin la base SQLite privada del entorno.')
p(d,'Para reproducir, instalar Python 3.12 y requirements.txt, ejecutar python -m pytest pruebas -q, python scripts/run_lab.py y python scripts/verify_evidence.py. Para abrir el tablero ejecutar python -m streamlit run app.py. Para MLflow usar python -m mlflow ui --backend-store-uri sqlite:///runtime/mlflow.db --host 127.0.0.1 --port 5088. El README contiene el procedimiento completo.')
p(d,'Los valores de tiempo y consumo dependen del host. Los textos y las etiquetas son históricos; no se publicó tráfico de clientes. Los spans son instrumentación JSON local. La evidencia demuestra la ejecución de este laboratorio y no un despliegue productivo de observabilidad distribuida.')
if (E/'streamlit.png').exists():image(d,'streamlit.png',6)
page(d);h(d,'Captura del registro en MLflow');image(d,'mlflow.png',6);p(d,'Captura del panel local: corrida finalizada, identificador, parámetros y etiquetas de alcance. Las métricas completas por paso se conservan en los exportes. Las trazas locales se registran como artefactos JSONL, no en la pestaña Traces de MLflow.')
save(d,'Evidencia_implementacion')

d=base('Simulación de incidentes y ejecución de runbooks')
h(d,'Diseño de la prueba')
p(d,'Preparé tres fallas reversibles dentro del servicio local, conservando intactos los pesos y el umbral del modelo. Las reglas y acciones se implementaron antes de ejecutar el laboratorio; este documento describe la ejecución y sus resultados. Utilicé un canario de 60 noticias históricas con etiquetas conocidas y solicitudes secuenciales.')
table(d,['Fase','Ventanas','Intervención'],[['Normal','0 a 2','Referencia sin falla'],['Latencia','3 a 6','Retraso de 350 ms; corrección tras ventana 4'],['Calidad','7 a 10','Probabilidad 1 − p; corrección tras ventana 8'],['Drift','11 a 14','Texto repetido ocho veces; corrección tras ventana 12']])
p(d,'La detección requiere dos ventanas consecutivas malas. La resolución requiere dos ventanas sanas. El hash SHA-256 del modelo se comprobó antes y después: '+s['model_sha256']+'. Las claves temporales se mantienen fuera de las evidencias.')
h(d,'Incidente de latencia')
p(d,f"Inyecté 350 ms adicionales por predicción. El p95 máximo de esta fase fue {max(z['latency_p95_ms'] for z in w if z['phase']=='latency'):.2f} ms. RB01 detectó burn rate excesivo, comprobó alcance y restauró mode=normal. La detección tomó {s['incidents'][0]['detection_seconds']:.3f} s; el cierre tras dos ventanas sanas tomó {s['incidents'][0]['recovery_seconds']:.3f} s desde la detección. Las 120 solicitudes lentas permanecen en el presupuesto histórico.")
p(d,'Acción preventiva: medir bajo concurrencia y definir ventanas temporales antes de producción. La prueba es de respuesta a retraso inyectado; no identifica un cuello de botella real de infraestructura.')
page(d);h(d,'Incidente de calidad')
p(d,'Invertí la probabilidad servida mediante 1 − p después de la inferencia. Así simulo una degradación de salida sin sustituir ni reentrenar el modelo. RB02 detectó la caída de recall o F1 con 20 etiquetas negativas por ventana, diagnosticó el modo de servicio y restauró la configuración normal.')
bad=[z for z in w if z['step'] in [7,8]];good=w[10]
table(d,['Estado','Recall','F1'],[['Antes','0.9500','0.9268'],['Durante',f"{bad[0]['recall']:.4f}",f"{bad[0]['f1']:.4f}"],['Después',f"{good['recall']:.4f}",f"{good['f1']:.4f}"]])
p(d,f"La detección tomó {s['incidents'][1]['detection_seconds']:.3f} s y la recuperación verificada {s['incidents'][1]['recovery_seconds']:.3f} s. No se atribuye la recuperación a entrenamiento ni a promoción de un modelo nuevo. Acción preventiva: añadir validación contractual de salida y mantener alerta abierta cuando no existan etiquetas suficientes.")
h(d,'Incidente de drift')
p(d,'Repetí ocho veces los textos del lote para desplazar su distribución de longitud. RB03 detectó PSI mayor a 0.20, puso en cuarentena el flujo sintético y volvió a usar la entrada de referencia. El escalamiento quedó como ticket local con reentrenamiento no ejecutado.')
p(d,f"El PSI máximo fue {max(z['length_psi'] for z in w):.3f}; volvió a {w[-1]['length_psi']:.3f}. La detección tomó {s['incidents'][2]['detection_seconds']:.3f} s y la recuperación verificada {s['incidents'][2]['recovery_seconds']:.3f} s. La prueba demuestra drift de longitud; no identifica un cambio conceptual ni exige por sí sola reentrenar.")
p(d,'Acción preventiva: observar otras variables, comprobar origen y calidad del lote y solicitar evaluación humana antes de actualizar el modelo. Una cuarentena productiva requeriría almacenamiento separado, permisos y política de recuperación; aquí se controla el generador local.')
page(d);h(d,'Cronología y cierre')
from datetime import datetime,timezone
fmt=lambda t:datetime.fromtimestamp(t,timezone.utc).strftime('%H:%M:%S.%f')[:-3]
table(d,['Caso','Inyección UTC','Detección UTC','Resolución UTC'],[[i['id'],fmt(i['injected_at']),fmt(i['detected_at']),fmt(i['resolved_at'])] for i in s['incidents']])
p(d,'Fecha UTC de la tabla: 6 de noviembre de 2026; fecha local de entrega: 5 de noviembre. MTTD medio 14.683 s; MTTR medio 0.273 s. La corrección exacta y las seis etapas de cada runbook están en evidencias/runbook_steps.json; incidentes completos en evidencias/incidents.json.')
h(d,'Resultados y decisiones')
p(d,'Los tres incidentes finalizaron resolved y el modelo conservó su hash. La corrida demuestra el ciclo de detectar, intervenir y verificar. La disponibilidad fue 100 %, mientras el SLO agregado de latencia quedó incumplido. No oculto ese resultado: es el efecto esperado de la falla deliberada y una prueba de que el presupuesto registra el daño incluso después de la recuperación.')
p(d,'Mantengo como límites la escala de un host, muestra repetida y etiquetas inmediatas. En un servicio real las etiquetas tardarían en llegar y las acciones necesitarían control de concurrencia, persistencia y guardias. Mi recomendación es validar esas condiciones antes de permitir que las señales apoyen decisiones operativas de clientes.')
h(d,'Cómo auditar')
p(d,'Revisar la configuración en config/alertas.json, los procedimientos en runbooks/README.md y las mediciones originales. Ejecutar python scripts/verify_evidence.py recalcula métricas y comprueba alertas, trazas, hash y recuperación. No es necesario confiar en las cifras impresas del reporte para contrastar el resultado.')
save(d,'Simulacion_incidentes')
print('Tres documentos creados')
