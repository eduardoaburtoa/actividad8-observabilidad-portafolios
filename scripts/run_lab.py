"""Ejecuta tráfico HTTP real, inyección controlada y runbooks locales; no reentrena."""
import hashlib,json,os,re,secrets,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
import requests
import mlflow
import psutil
from mlflow.tracking import MlflowClient
from observabilidad.monitor import Alerts,metrics

def main():
    out=ROOT/'evidencias';out.mkdir(exist_ok=True);runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True)
    config=json.loads((ROOT/'config/alertas.json').read_text()); frame=pd.read_csv(ROOT/'datos/predicciones_test.csv')
    sample=pd.concat([frame[frame.y==1].sample(20,random_state=42),frame[frame.y==0].sample(40,random_state=42)]).sample(frac=1,random_state=42)
    reference=[len(re.findall(r'\b\w+\b',t)) for t in sample.texto]
    sample[['id','y']].to_csv(out/'muestra_canario.csv',index=False)
    expected=json.loads((ROOT/'modelos/manifest.json').read_text())
    model_hash=hashlib.sha256((ROOT/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()
    assert model_hash==expected['sha256'], 'El modelo no coincide con el manifest'
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    env=dict(os.environ,API_TOKEN=secrets.token_urlsafe(32),LAB_TOKEN=secrets.token_urlsafe(32),LAB_MODE='1',TELEMETRY_DIR=str(runtime))
    base=f'http://127.0.0.1:{port}'; headers={'X-API-Key':env['API_TOKEN']};labheaders={'X-Lab-Token':env['LAB_TOKEN']}
    # Cada ejecución conserva directorio propio de telemetría.
    session=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());rt=runtime/session;rt.mkdir();env['TELEMETRY_DIR']=str(rt)
    serverlog=(rt/'server.log').open('w');server=subprocess.Popen([sys.executable,'-m','uvicorn','observabilidad.service:app','--host','127.0.0.1','--port',str(port),'--no-access-log'],cwd=ROOT,env=env,stdout=serverlog,stderr=subprocess.STDOUT)
    def control(mode):
        r=requests.post(base+'/lab/control',headers=labheaders,json={'mode':mode},timeout=10);r.raise_for_status();d=r.json();assert d['model_sha256']==model_hash;return d
    windows=[];events=[];alerts=[];actions=[];incidents=[];engine=Alerts(config);drift_input=False
    process=psutil.Process(server.pid);process.cpu_percent()
    def action(record):
        actions.append({'time':time.time(),'session':session,**record})
        (out/'runbook_steps.json').write_text(json.dumps(actions,ensure_ascii=False,indent=2))
    try:
        for _ in range(200):
            if server.poll() is not None:raise RuntimeError('API no arrancó; consultar runtime')
            try:
                if requests.get(base+'/health',timeout=1).ok:break
            except requests.RequestException:pass
            time.sleep(.1)
        else:raise TimeoutError('API no disponible')
        mlflow.set_tracking_uri('sqlite:///'+str(runtime/'mlflow.db'));mlflow.set_experiment('Actividad8_observabilidad_portafolios')
        with mlflow.start_run(run_name='game_day_'+session) as run:
            mlflow.log_params({**config,'model_sha256':model_hash,'seed':42,'canary':'20 negativas + 40 no negativas; test retrospectivo con etiquetas conocidas','source_commit':'b6ecb7a0e6b01ece989369b7b67178fe7d7cc2a4'})
            phases=[('normal',3),('latency',4),('degradation',4),('drift',4)]
            step=0
            for phase,count in phases:
                start=time.time(); incident=None
                if phase!='normal':
                    incident={'id':'INC-'+str(len(incidents)+1).zfill(3),'type':phase,'injected_at':start,'detected_at':None,'corrected_at':None,'resolved_at':None,'status':'injected'};incidents.append(incident)
                    control('normal' if phase=='drift' else phase);drift_input=phase=='drift'
                    action({'incident':incident['id'],'stage':'prepare','detail':'Inyección autorizada sólo en laboratorio; artefacto intacto.'})
                for _ in range(count):
                    batch=[];window_start=time.time()
                    for row in sample.itertuples():
                        text=(row.texto+' ')*8 if drift_input else row.texto
                        tick=time.perf_counter(); status=0;prob=None;trace=None
                        try:
                            response=requests.post(base+'/v1/predict',headers=headers,json={'texto':text,'idioma':'en'},timeout=5)
                            status=response.status_code;trace=response.headers.get('X-Trace-ID')
                            if status==200:prob=response.json()['probabilidad_negativa']
                        except requests.RequestException:pass
                        e={'step':step,'phase':phase,'sample_id':row.id,'timestamp':time.time(),'status':status,'duration_ms':(time.perf_counter()-tick)*1000,'probability':prob,'y':int(row.y),'length':len(re.findall(r'\b\w+\b',text)),'trace_id':trace}
                        batch.append(e);events.append(e)
                    measured=metrics(batch,reference,config);measured.update({'step':step,'phase':phase,'timestamp':time.time(),'window_seconds':time.time()-window_start,'requests_per_second':len(batch)/(time.time()-window_start)})
                    notices=engine.evaluate(measured,step);alerts.extend(notices)
                    for notice in notices:
                        key=notice['key'];now=time.time()
                        if notice['state']=='open':
                            action({'incident':incident['id'] if incident else 'baseline','stage':'detect','rule':key,'priority':notice['priority'],'step':step})
                            if incident and incident['detected_at'] is None:incident['detected_at']=now;incident['status']='detected'
                            action({'incident':incident['id'] if incident else 'baseline','stage':'diagnose','detail':'Comparar SLI, versión, hash y trazas; comprobar inyección y alcance.'})
                            if key in ['latency','quality','availability']:
                                result=control('normal');action({'incident':incident['id'] if incident else 'baseline','stage':'correct','action':'rollback_configuration','result':result})
                            elif key=='drift':
                                drift_input=False;ticket={'incident':incident['id'],'decision':'cuarentena del lote simulado y restauración de flujo de referencia; revisión de datos antes de reentrenar','retraining_executed':False}
                                action({'incident':incident['id'],'stage':'correct','action':'quarantine_and_escalate','result':ticket})
                            if incident:incident['corrected_at']=time.time();incident['status']='corrected'
                        elif notice['state']=='resolved':
                            action({'incident':incident['id'] if incident else 'baseline','stage':'verify','rule':key,'detail':'Dos ventanas consecutivas recuperadas; no restituye presupuesto histórico consumido.'})
                            if incident:incident['resolved_at']=now;incident['status']='resolved'
                    measured['rss_mb']=process.memory_info().rss/1024**2
                    measured['memory_budget_utilization']=measured['rss_mb']/config['memory_budget_mb']
                    measured['cpu_percent_process']=process.cpu_percent()
                    measured['active_alerts']=len(engine.active);windows.append(measured)
                    mlflow.log_metrics({k:float(v) for k,v in measured.items() if isinstance(v,(int,float))},step=step)
                    for name,data in [('windows.json',windows),('alerts.json',alerts),('incidents.json',incidents)]:
                        temp=out/(name+'.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(out/name)
                    print(f"step={step} phase={phase} p95={measured['latency_p95_ms']:.1f} recall={measured['recall']:.3f} psi={measured['length_psi']:.3f} alerts={len(engine.active)}",flush=True);step+=1
                if incident:
                    incident['detection_seconds']=incident['detected_at']-start if incident['detected_at'] else None
                    incident['recovery_seconds']=incident['resolved_at']-incident['detected_at'] if incident['resolved_at'] and incident['detected_at'] else None
                    action({'incident':incident['id'],'stage':'postmortem','detail':'Registrar causa inyectada, detección, corrección, recuperación y límites; mantener aprobación humana para modelo nuevo.'})
            for name in ['logs.jsonl','traces.jsonl','actions.jsonl']:(out/name).write_bytes((rt/name).read_bytes())
            (out/'requests.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
            total=len(events);bad=sum(e['status']!=200 for e in events);slow=sum(e['status']!=200 or e['duration_ms']>config['latency_limit_ms'] for e in events)
            summary={'session':session,'model_sha256':model_hash,'requests':total,'windows':len(windows),'mlflow_run_id':run.info.run_id,'mlflow_experiment_id':run.info.experiment_id,'raw_notifications':engine.raw,'emitted_notifications':engine.emitted,'suppressed_notifications':engine.suppressed,'noise_reduction_fraction':engine.suppressed/engine.raw if engine.raw else 0,'availability_budget_allowed':total*(1-config['availability_slo']),'availability_budget_used':bad,'latency_budget_allowed':total*(1-config['latency_slo']),'latency_budget_used':slow,'incidents':incidents,'all_recovered':all(i['status']=='resolved' for i in incidents),'mttd_seconds':sum(i['detection_seconds'] for i in incidents if i['detection_seconds'] is not None)/len(incidents),'mttr_seconds':sum(i['recovery_seconds'] for i in incidents if i['recovery_seconds'] is not None)/len(incidents),'scope':'laboratorio local con solicitudes reales y fallas inyectadas; no tráfico de clientes ni SLO mensual validado'}
            (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(out/'incidents.json').write_text(json.dumps(incidents,ensure_ascii=False,indent=2))
            
            for name in ['summary.json','windows.json','alerts.json','incidents.json','runbook_steps.json','requests.jsonl','logs.jsonl','traces.jsonl','actions.jsonl','muestra_canario.csv']:
                mlflow.log_artifact(str(out/name),artifact_path='evidencias')
            mlflow.log_artifact(str(ROOT/'config/alertas.json'),artifact_path='config')
            mlflow.set_tags({'scope':'simulacion_academica','model_changed':'false','retraining':'not_executed'})
        client=MlflowClient();saved=client.get_run(run.info.run_id)
        export={'run_id':saved.info.run_id,'status':saved.info.status,'params':saved.data.params,'metrics':saved.data.metrics,'tags':saved.data.tags,'artifacts':[a.path for a in client.list_artifacts(saved.info.run_id,'evidencias')]}
        (out/'mlflow_export.json').write_text(json.dumps(export,ensure_ascii=False,indent=2))
        assert summary['all_recovered'], 'Hay incidentes sin recuperar; revisar evidencia'
        assert hashlib.sha256((ROOT/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()==model_hash
        print(json.dumps(summary,ensure_ascii=False,indent=2))
    finally:server.terminate();server.wait(timeout=15);serverlog.close()
if __name__=='__main__':main()
