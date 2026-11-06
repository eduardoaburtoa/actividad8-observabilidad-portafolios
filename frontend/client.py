import os,requests
class BackendError(Exception):pass
def call(path,payload=None):
    url=os.environ.get('API_URL','http://127.0.0.1:8000').rstrip('/')+path
    try:
        r=requests.request('POST' if payload is not None else 'GET',url,json=payload,headers={'X-API-Key':os.environ.get('API_TOKEN','')},timeout=(3,20))
        if not r.ok:
            detail=r.json().get('detail','Solicitud rechazada')
            raise BackendError(f'API {r.status_code}: {detail}')
        return r.json()
    except (requests.RequestException,ValueError) as exc:
        raise BackendError('No fue posible conectar con la API. Comprueba que el servicio esté listo.') from exc
