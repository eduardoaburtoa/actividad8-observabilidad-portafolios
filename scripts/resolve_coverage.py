"""Resolve coverage references from rendered PDFs without executing report builder."""
from pathlib import Path
import ast,json,sys
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
source=ast.parse((R/'scripts/build_reports.py').read_text())
coverage=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='COVERAGE' for t in n.targets))
base=Path(sys.argv[1]) if len(sys.argv)>1 else R/'documentos'
out={}
for name,sections in coverage.items():
 path=base/f'{name}.pdf'
 if not path.exists():path=base/name/f'{name}.pdf'
 pages=[' '.join(p.extract_text().split()) for p in PdfReader(path).pages]
 out[name]={}
 for section in sections:
  matches=[i+1 for i,t in enumerate(pages) if section in t and 'Cobertura de la rúbrica' not in t]
  if not matches:raise ValueError(f'Missing section: {name}: {section}')
  out[name][section]=matches[0]
(R/'documentos/coverage_pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
