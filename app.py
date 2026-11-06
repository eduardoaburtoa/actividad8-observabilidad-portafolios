"""Tablero operativo con actualización periódica y evidencia reproducible."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Vértice AI · Observabilidad',layout='wide')
st.image(str(ROOT/'documentos/vertice_logo.png'),width=100)
st.title('Actividad 8 · Continuidad del servicio')
st.caption('Eduardo Aburto Angulo · Laboratorio académico · Las alertas requieren revisión humana; no son órdenes de inversión.')
def read(name,default):
    path=ROOT/'evidencias'/name
    return json.loads(path.read_text()) if path.exists() else default
@st.fragment(run_every='3s')
def dashboard():
    rows=read('windows.json',[])
    if not rows:st.info('Ejecuta python scripts/run_lab.py para generar y observar la telemetría.');return
    d=pd.DataFrame(rows);last=d.iloc[-1];a,b,c,e=st.columns(4)
    a.metric('Disponibilidad última ventana',f"{last.availability:.1%}");b.metric('Latencia p95',f"{last.latency_p95_ms:.1f} ms");c.metric('Recall canario etiquetado',f"{last.recall:.1%}");e.metric('Alertas activas',int(last.active_alerts))
    st.caption('Ventanas de 60 solicitudes. Refresco cada 3 segundos; con el laboratorio detenido se muestra la última corrida, no tráfico vivo.')
    t1,t2,t3,t4=st.tabs(['Servicio y presupuesto','Modelo y drift','Incidentes y runbooks','Trazabilidad'])
    with t1:
        st.line_chart(d.set_index('step')[['latency_p95_ms']]);st.line_chart(d.set_index('step')[['latency_burn','availability_burn']]);st.dataframe(d[['step','phase','requests','latency_budget_remaining','availability_budget_remaining','requests_per_second']],hide_index=True)
        if 'rss_mb' in d:
            st.line_chart(d.set_index('step')[['rss_mb']]);st.caption('Memoria RSS real del proceso; presupuesto de planificación 512 MB, no límite impuesto al host.')
        st.info('El presupuesto negativo refleja consumo excesivo. Recuperar el servicio no borra el consumo histórico. SLO del laboratorio: 99 %; latencia ≤250 ms. No es un SLA contratado.')
    with t2:
        st.line_chart(d.set_index('step')[['precision','recall','f1']]);st.line_chart(d.set_index('step')[['length_psi']]);st.warning('Calidad calculada con etiquetas históricas conocidas. Drift de longitud no demuestra pérdida de calidad ni concept drift. El modelo sólo procesa noticias en inglés.')
    with t3:
        st.dataframe(pd.DataFrame(read('alerts.json',[])),hide_index=True);st.dataframe(pd.DataFrame(read('incidents.json',[])),hide_index=True)
        st.json(read('runbook_steps.json',[]),expanded=False)
    with t4:
        st.json(read('summary.json',{}),expanded=False);st.json(read('mlflow_export.json',{}),expanded=False)
        path=ROOT/'evidencias/traces.jsonl'
        if path.exists():
            traces=[json.loads(x) for x in path.read_text().splitlines()];st.dataframe(pd.DataFrame(traces[-30:]),hide_index=True)
        st.caption('Logs y trazas correlacionados por trace_id; no se almacenan texto de noticias, claves ni datos de clientes en la telemetría.')
dashboard()
