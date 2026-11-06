"""SLI por solicitud, deriva descriptiva y alertas con persistencia y recuperación."""
import math
from collections import Counter
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

def psi(reference,current,bins):
    a=np.histogram(reference,bins=bins)[0]+.5;b=np.histogram(current,bins=bins)[0]+.5
    a=a/a.sum();b=b/b.sum();return float(np.sum((b-a)*np.log(b/a)))

def metrics(events,reference_lengths,config):
    n=len(events); ok=[e for e in events if e['status']==200];bad=sum(e['status']!=200 for e in events)
    slow=sum(e['status']!=200 or e['duration_ms']>config['latency_limit_ms'] for e in events)
    labels=[e for e in ok if e.get('y') is not None];y=[e['y'] for e in labels];pred=[e['probability']>=.20 for e in labels]
    availability=1-bad/n if n else None;latency=1-slow/n if n else None
    out={'requests':n,'eligible_labels':len(labels),'negative_labels':sum(y),'server_errors':bad,'slow_or_failed':slow,
         'availability':availability,'latency_compliance':latency,'latency_p95_ms':float(np.percentile([e['duration_ms'] for e in events],95)) if n else None,
         'availability_burn':(1-availability)/(1-config['availability_slo']) if n else None,
         'latency_burn':(1-latency)/(1-config['latency_slo']) if n else None,
         'availability_budget_remaining':n*(1-config['availability_slo'])-bad,
         'latency_budget_remaining':n*(1-config['latency_slo'])-slow,
         'precision':float(precision_score(y,pred,zero_division=0)) if labels else None,
         'recall':float(recall_score(y,pred,zero_division=0)) if labels else None,
         'f1':float(f1_score(y,pred,zero_division=0)) if labels else None,
         'length_psi':psi(reference_lengths,[e['length'] for e in events],config['length_bins']) if n else None}
    return out

class Alerts:
    def __init__(self,config):self.c=config;self.bad=Counter();self.good=Counter();self.active=set();self.raw=0;self.emitted=0;self.suppressed=0
    def evaluate(self,m,step):
        if m['requests']<self.c['minimum_samples']:return []
        quality=m['negative_labels']>=self.c['quality_min_negative_labels']
        flags={'availability':m['availability_burn']>self.c['burn_rate_trigger'],
               'latency':m['latency_burn']>self.c['burn_rate_trigger'],
               'quality':(m['recall']<self.c['quality_min_recall'] or m['f1']<self.c['quality_min_f1']) if quality else None,
               'drift':m['length_psi']>self.c['drift_psi_trigger']}
        out=[]
        for key,failed in flags.items():
            if failed is None:continue
            if failed:
                self.raw+=1;self.bad[key]+=1;self.good[key]=0
                if self.bad[key]>=self.c['consecutive_windows'] and key not in self.active:
                    self.active.add(key);self.emitted+=1;out.append({'step':step,'key':key,'state':'open','priority':'P1' if key=='availability' else 'P2' if key in ['latency','quality'] else 'P3'})
                else:self.suppressed+=1
            else:
                self.bad[key]=0;self.good[key]+=1
                if key in self.active and self.good[key]>=self.c['recovery_windows']:
                    self.active.remove(key);out.append({'step':step,'key':key,'state':'resolved','priority':'recovery'})
        return out
