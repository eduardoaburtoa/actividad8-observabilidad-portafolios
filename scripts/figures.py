"""Gráficas exclusivamente a partir de las mediciones exportadas."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]; E=R/'evidencias'
w=json.loads((E/'windows.json').read_text());x=[r['step'] for r in w]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#072146'})
fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
for ax,key,title,limit in zip(axes,['latency_p95_ms','recall','length_psi'],['Latencia p95 observada (ms)','Recall de la clase negativa','PSI de longitud'],[250,.75,.2]):
 ax.plot(x,[r[key] for r in w],'-o',color='#004481');ax.axhline(limit,color='#da3851',ls='--',label=f'Umbral {limit}');ax.set_ylabel(title);ax.grid(alpha=.2);ax.legend(loc='upper right')
 for a,b in [(3,4),(7,8),(11,12)]:ax.axvspan(a-.3,b+.3,color='#f8cd51',alpha=.18)
axes[-1].set_xlabel('Ventana de 60 solicitudes · amarillo = falla inyectada')
fig.suptitle('Actividad 8 · Detección y recuperación medidas',color='#004481',fontweight='bold');fig.tight_layout();fig.savefig(E/'dashboard_mediciones.png',dpi=160);plt.close(fig)
s=json.loads((E/'summary.json').read_text());fig,ax=plt.subplots(1,2,figsize=(10,3.7))
ax[0].bar(['Permitidas','Consumidas'],[s['latency_budget_allowed'],s['latency_budget_used']],color=['#004481','#da3851']);ax[0].set_title('Presupuesto de latencia en 900 solicitudes');ax[0].set_ylabel('Solicitudes')
ax[1].bar(['Sin persistencia','Alertas emitidas'],[s['raw_notifications'],s['emitted_notifications']],color=['#5bbeff','#004481']);ax[1].set_title('Avisos por ventanas con incumplimiento');fig.tight_layout();fig.savefig(E/'presupuesto_alertas.png',dpi=160);plt.close(fig)
