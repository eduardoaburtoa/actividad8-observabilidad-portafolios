"""Servicio instrumentado de laboratorio; conserva el artefacto y la API de Fase II."""
import asyncio
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import Literal
from backend.main import app
ROOT=Path(__file__).resolve().parents[1]
STATE={'mode':'normal','revision':0}
CONFIG=json.loads((ROOT/'config/alertas.json').read_text())
OUT=Path(os.environ.get('TELEMETRY_DIR',ROOT/'runtime'))
OUT.mkdir(parents=True,exist_ok=True)
def emit(name,record):
    with (OUT/name).open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
@app.middleware('http')
async def telemetry(request: Request, call_next):
    trace=uuid.uuid4().hex; parent=uuid.uuid4().hex[:16]; start=time.perf_counter_ns(); now=time.time_ns()
    mode=STATE['mode']; status=500; error=False
    try:
        if request.url.path=='/v1/predict' and mode=='latency':await asyncio.sleep(CONFIG['lab_delay_seconds'])
        child_start=time.perf_counter_ns(); response=await call_next(request); child_end=time.perf_counter_ns()
        status=response.status_code
        if request.url.path=='/v1/predict' and mode=='degradation' and status==200:
            raw=b''.join([chunk async for chunk in response.body_iterator]);data=json.loads(raw)
            data['probabilidad_negativa']=1-data['probabilidad_negativa'];data['priorizar_revision']=data['probabilidad_negativa']>=.20
            data['simulacion_incidente']=True
            response=JSONResponse(data,status_code=status)
        response.headers['X-Trace-ID']=trace
        return response
    except Exception:
        error=True;raise
    finally:
        end=time.perf_counter_ns(); duration=(end-start)/1e6
        record={'timestamp_ns':now,'trace_id':trace,'span_id':parent,'route':request.url.path,'method':request.method,'status':status,'duration_ms':duration,'mode':mode,'revision':STATE['revision'],'error':error}
        emit('logs.jsonl',record)
        emit('traces.jsonl',{**record,'name':'http.server','parent_span_id':None,'start_ns':now,'end_ns':now+end-start})
        if 'child_end' in locals():emit('traces.jsonl',{'trace_id':trace,'span_id':uuid.uuid4().hex[:16],'parent_span_id':parent,'name':'api.dispatch','start_ns':now+child_start-start,'end_ns':now+child_end-start,'duration_ms':(child_end-child_start)/1e6})
class Control(BaseModel):
    model_config=ConfigDict(extra='forbid')
    mode:Literal['normal','latency','degradation']
@app.post('/lab/control')
def control(payload:Control,request:Request):
    if os.environ.get('LAB_MODE')!='1':raise HTTPException(404,'Laboratorio desactivado')
    if request.headers.get('X-Lab-Token')!=os.environ.get('LAB_TOKEN') or not os.environ.get('LAB_TOKEN'):raise HTTPException(401,'Control no autorizado')
    old=STATE['mode'];STATE['mode']=payload.mode;STATE['revision']+=1
    evidence={'previous':old,**STATE,'model_sha256':hashlib.sha256((ROOT/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()}
    emit('actions.jsonl',{'timestamp_ns':time.time_ns(),'action':'set_mode',**evidence})
    return evidence
