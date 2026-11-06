"""Recalcula evidencia publicada, sin depender de una base MLflow local."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from observabilidad.monitor import metrics,Alerts
E=R/'evidencias';load=lambda n:json.loads((E/n).read_text())
s=load('summary.json');w=load('windows.json');c=json.loads((R/'config/alertas.json').read_text())
r=[json.loads(x) for x in (E/'requests.jsonl').read_text().splitlines()]
assert len(r)==s['requests']==900 and len(w)==15
assert hashlib.sha256((R/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()==s['model_sha256']==json.loads((R/'modelos/manifest.json').read_text())['sha256']
a=Alerts(c);notices=[];reference=[x['length'] for x in r if x['step']==0]
for row in w:
 m=metrics([x for x in r if x['step']==row['step']],reference,c)
 for key,val in m.items():assert abs(val-row[key])<1e-9,(key,row['step'])
 notices.extend(a.evaluate(m,row['step']))
assert notices==load('alerts.json')
assert (a.raw,a.emitted,a.suppressed)==(s['raw_notifications'],s['emitted_notifications'],s['suppressed_notifications'])
assert s['latency_budget_used']==sum(x['duration_ms']>c['latency_limit_ms'] or x['status']!=200 for x in r)
assert s['availability_budget_used']==sum(x['status']!=200 for x in r)
t=[json.loads(x) for x in (E/'traces.jsonl').read_text().splitlines()];ids={x['trace_id'] for x in t}
assert all(x['trace_id'] in ids for x in r)
spans={x['span_id'] for x in t};assert all(not x.get('parent_span_id') or x['parent_span_id'] in spans for x in t)
assert all(x['end_ns']>=x['start_ns'] for x in t)
for i in s['incidents']:
 assert i['injected_at']<=i['detected_at']<=i['corrected_at']<=i['resolved_at'] and i['status']=='resolved'
 assert abs(i['recovery_seconds']-(i['resolved_at']-i['detected_at']))<1e-9
 assert {x['stage'] for x in load('runbook_steps.json') if x['incident']==i['id']} >= {'prepare','detect','diagnose','correct','verify','postmortem'}
export=load('mlflow_export.json');assert export['status']=='FINISHED' and export['run_id']==s['mlflow_run_id']
assert export['params']['model_sha256']==s['model_sha256'] and 'evidencias/requests.jsonl' in export['artifacts']
print('OK: 900 solicitudes, 15 ventanas, métricas recalculadas, trazas correlacionadas, 3 runbooks y MLflow FINISHED.')
