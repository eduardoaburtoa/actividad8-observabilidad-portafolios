"""Deriva tiempos y exposición de evidencias congeladas; nunca llama al servicio."""
from pathlib import Path
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidencias'

def calculate():
    incidents = json.loads((E / 'incidents.json').read_text())
    requests = [json.loads(line) for line in (E / 'requests.jsonl').read_text().splitlines()]
    rows = []
    for item in incidents:
        exposed = [r for r in requests if item['injected_at'] <= r['timestamp'] <= item['detected_at']]
        rows.append({'id': item['id'], 'type': item['type'],
                     'detection_seconds': item['detected_at'] - item['injected_at'],
                     'recovery_seconds': item['resolved_at'] - item['detected_at'],
                     'completed_requests_before_detection': len(exposed),
                     'slow_completed_requests_before_detection': sum(r['duration_ms'] > 250 for r in exposed),
                     'unique_sample_ids_before_detection': len({r['sample_id'] for r in exposed})})
    out = {'method': 'Timestamp de finalización entre inyección y detección, inclusive. Lenta: duración >250 ms. Solicitudes repetidas, no clientes únicos.',
           'source_sha256': {name: hashlib.sha256((E/name).read_bytes()).hexdigest() for name in ['incidents.json','requests.jsonl']},
           'incidents': rows}
    for metric in ['detection_seconds', 'recovery_seconds']:
        values = [r[metric] for r in rows]
        out[metric] = {'mean': statistics.mean(values), 'median': statistics.median(values), 'max': max(values)}
    return out

if __name__ == '__main__':
    result = calculate()
    (E/'incident_analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
