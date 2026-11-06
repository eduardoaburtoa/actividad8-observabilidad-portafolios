import hashlib,json
from pathlib import Path
from fastapi.testclient import TestClient
from observabilidad.service import app,STATE
ROOT=Path(__file__).parents[1]
def test_controls_and_trace_privacy(monkeypatch,tmp_path):
    import observabilidad.service as s
    monkeypatch.setattr(s,'OUT',tmp_path);monkeypatch.setenv('API_TOKEN','academic-api-test-token');monkeypatch.setenv('LAB_TOKEN','academic-lab');monkeypatch.setenv('LAB_MODE','1');STATE['mode']='normal'
    before=hashlib.sha256((ROOT/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()
    with TestClient(app) as c:
        assert c.post('/lab/control',json={'mode':'degradation'}).status_code==401
        h={'X-API-Key':'academic-api-test-token'};payload={'texto':'Operating profit fell sharply.','idioma':'en'}
        first=c.post('/v1/predict',headers=h,json=payload);assert first.status_code==200 and first.headers['X-Trace-ID']
        assert c.post('/lab/control',headers={'X-Lab-Token':'academic-lab'},json={'mode':'degradation'}).status_code==200
        second=c.post('/v1/predict',headers=h,json=payload);assert abs(second.json()['probabilidad_negativa']+first.json()['probabilidad_negativa']-1)<1e-12
        c.post('/lab/control',headers={'X-Lab-Token':'academic-lab'},json={'mode':'normal'})
        final=c.post('/v1/predict',headers=h,json=payload);assert final.json()['probabilidad_negativa']==first.json()['probabilidad_negativa']
        monkeypatch.setenv('LAB_MODE','0');assert c.post('/lab/control',headers={'X-Lab-Token':'academic-lab'},json={'mode':'degradation'}).status_code==404
    logs=(tmp_path/'logs.jsonl').read_text();assert 'academic-api-test-token' not in logs and payload['texto'] not in logs
    spans=[json.loads(x) for x in (tmp_path/'traces.jsonl').read_text().splitlines()];assert any(x['parent_span_id'] for x in spans)
    assert hashlib.sha256((ROOT/'modelos/modelo_SVM_calibrada.joblib').read_bytes()).hexdigest()==before
