"""Compare document structure against frozen audited commit; no lab execution."""
from pathlib import Path
import io,json,subprocess,zipfile
from lxml import etree
R=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
NAMES=['Documento_tecnico','Evidencia_implementacion','Simulacion_incidentes']
SECTIONS=['Indicadores y contratos de medición','Alertas y reducción de ruido','Dashboard para decidir','Runbooks de respuesta a incidentes','Data drift y límites del diagnóstico','Respuesta automatizada y gobernanza']
def inspect(data):
 root=etree.fromstring(zipfile.ZipFile(io.BytesIO(data)).read('word/document.xml'))
 paras=[''.join(p.itertext()) for p in []]
 paras=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in root.xpath('./w:body/w:p',namespaces=NS)]
 return {'numbered_figures':sum(t.startswith('Figura ') for t in paras),'references_sections':paras.count('Referencias'),'explicit_required_sections':{h:h in paras for h in SECTIONS}}
def main():
 out={}
 for n in NAMES:
  path=f'documentos/{n}.docx'
  before=subprocess.check_output(['git','show',f'b7ec2a0:{path}'],cwd=R)
  out[n]={'before':inspect(before),'after':inspect((R/path).read_bytes())}
 out['method']='Seis apartados medidos por encabezado propio exacto en el documento técnico; referencias cuenta encabezado Referencias (no ausencia de fuentes); figuras cuenta pies Figura N.'
 (R/'evidencias/document_revision_comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
