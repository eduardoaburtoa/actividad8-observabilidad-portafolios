"""Audit final DOCX/PDF content and coverage without changing frozen evidence.

Optional dependency: pypdf. Google Docs readback is audited separately at export.
"""
from pathlib import Path
import json,re,zipfile,xml.etree.ElementTree as ET
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def normalized(text):return re.sub(r'\s+','',text).replace('\u00ad','')
def paragraphs(path):
 with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('word/document.xml'))
 return [''.join(t.text or '' for t in p.findall('.//w:t',NS)) for p in root.findall('.//w:p',NS)]
def main():
 coverage=json.loads((ROOT/'documentos/coverage_pages.json').read_text())
 for name,sections in coverage.items():
  paras=paragraphs(ROOT/f'documentos/{name}.docx')
  pages=[p.extract_text() for p in PdfReader(ROOT/f'documentos/{name}.pdf').pages]
  text=normalized(''.join(pages))
  missing=[p for p in paras if normalized(p) and normalized(p) not in text]
  assert not missing,(name,missing)
  assert paras.count('Referencias')==1,name
  assert sum(p.count('ánimo') for p in paras)==1,name
  assert 'La IA no sustituye el criterio del banquero; lo aumenta.' in paras,name
  for heading,page in sections.items():assert normalized(heading) in normalized(pages[page-1]),(name,heading,page)
  print(f'{name}: {len(pages)} páginas; texto DOCX/PDF y cobertura correctos.')
if __name__=='__main__':main()
