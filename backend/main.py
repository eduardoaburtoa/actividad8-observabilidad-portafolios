"""API académica. No registra texto, identidades ni credenciales."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
import hashlib,json,os,secrets
import joblib,pandas as pd
from fastapi import FastAPI,Depends,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field,field_validator
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'modelos/manifest.json').read_text())
MODEL=None
NOTICE='Priorizar revisión humana; no es orden de inversión ni predicción de rendimiento.'
@asynccontextmanager
async def lifespan(app):
    global MODEL
    token=os.environ.get('API_TOKEN','')
    if len(token)<16: raise RuntimeError('Configura API_TOKEN con al menos 16 caracteres.')
    path=ROOT/'modelos/modelo_SVM_calibrada.joblib'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=MANIFEST['sha256']:
        raise RuntimeError('Integridad del modelo incorrecta')
    MODEL=joblib.load(path)
    yield
    MODEL=None
app=FastAPI(title='Vértice AI Fase II',version='1.0.0',lifespan=lifespan)
def auth(x_api_key:str=Header(default='')):
    if not secrets.compare_digest(x_api_key,os.environ.get('API_TOKEN','')) or not x_api_key:
        raise HTTPException(401,'Credencial inválida')
class Input(BaseModel):
    model_config=ConfigDict(extra='forbid')
    texto:str=Field(min_length=3,max_length=4000)
    idioma:Literal['en']='en'
    @field_validator('texto')
    @classmethod
    def clean(cls,v):
        v=v.strip()
        if len(v)<3 or not any(c.isalpha() for c in v):raise ValueError('Se requiere una noticia con texto')
        return v
class Scenario(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    cliente_id:str=Field(pattern=r'^C\d{3}$')
    proporcion:float=Field(gt=0,le=1)
    mejora_anual_pp:float=Field(ge=-100,le=100)
    meses:int=Field(ge=1,le=120)
    gastos_adicionales_anuales_pp:float=Field(ge=0,le=100)
    perfil_destino:Literal['Conservador','Moderado','Agresivo']
def clients():return pd.read_csv(ROOT/'contexto/clientes_simulados.csv')
@app.get('/health')
def health():
    if MODEL is None:raise HTTPException(503,'Modelo no disponible')
    return {'status':'ok','model_ready':True,'version':'1.0.0'}
@app.get('/v1/model',dependencies=[Depends(auth)])
def model():return {**MANIFEST,'notice':NOTICE,'joint_target_met':False}
@app.post('/v1/predict',dependencies=[Depends(auth)])
def predict(data:Input):
    if MODEL is None:raise HTTPException(503,'Modelo no disponible')
    # Los tres calibradores contienen su propio vocabulario TF-IDF.
    if not any(c.estimator.steps[0][1].transform([data.texto]).nnz for c in MODEL.calibrated_classifiers_):
        raise HTTPException(422,'Texto fuera de vocabulario; requiere revisión sin inferencia fiable')
    prob=float(MODEL.predict_proba([data.texto])[0,1])
    return {'probabilidad_negativa':prob,'umbral':0.2,'priorizar_revision':prob>=0.2,'idioma_declarado':'en','notice':NOTICE,'model_sha256':MANIFEST['sha256']}
@app.get('/v1/clients',dependencies=[Depends(auth)])
def get_clients():return {'simulados':True,'clientes':clients().to_dict('records')}
@app.post('/v1/scenario',dependencies=[Depends(auth)])
def scenario(data:Scenario):
    rows=clients();rows=rows[rows.cliente_id==data.cliente_id]
    if rows.empty:raise HTTPException(404,'Cliente simulado inexistente')
    c=rows.iloc[0];compatible=c.perfil_riesgo==data.perfil_destino
    amount=float(c.posicion_mxn)*data.proporcion
    benefit=amount*data.mejora_anual_pp/100*data.meses/12
    fees=amount*data.gastos_adicionales_anuales_pp/100*data.meses/12
    brokerage=amount*.02
    net=benefit-fees-brokerage
    return {'simulado':True,'perfil_compatible':bool(compatible),'monto_migrado_mxn':amount,'mejora_supuesta_mxn':benefit,'corretaje_supuesto_mxn':brokerage,'gastos_adicionales_mxn':fees,'beneficio_incremental_supuesto_mxn':net,'elegible_para_revision':bool(compatible and net>0),'supuesto':'1 % compra + 1 % venta sobre el mismo nocional. Cálculo lineal, sin impuestos ni garantía. Gastos adicionales sólo si no están ya descontados del rendimiento. No equivale al ingreso neto del banco.','notice':NOTICE}
