import json
from pathlib import Path
import pytest
from observabilidad.monitor import Alerts,metrics,psi
C=json.loads((Path(__file__).parents[1]/'config/alertas.json').read_text())
def events(n=60,latency=5,status=200,labels=True):
    return [{'status':status,'duration_ms':latency,'length':20,'y':int(i%2==0) if labels else None,'probability':.9 if i%2==0 else .05} for i in range(n)]
def test_budget_formula_and_failed_requests():
    e=events();e[0]['status']=500
    m=metrics(e,[20]*60,C)
    assert m['availability']==pytest.approx(59/60)
    assert m['availability_budget_remaining']==pytest.approx(-.4)
    assert m['availability_burn']==pytest.approx(1/.6)
def test_latency_not_mean_and_budget_not_reset():
    m=metrics(events(latency=300),[20]*60,C)
    assert m['latency_compliance']==0 and m['latency_burn']==pytest.approx(100)
    assert m['latency_budget_remaining']==pytest.approx(-59.4)
def test_persistence_deduplication_and_recovery():
    a=Alerts(C);bad=metrics(events(latency=300),[20]*60,C);good=metrics(events(),[20]*60,C)
    assert a.evaluate(bad,0)==[]
    assert a.evaluate(bad,1)[0]['state']=='open'
    assert a.evaluate(bad,2)==[]
    assert a.evaluate(good,3)==[]
    assert a.evaluate(good,4)[0]['state']=='resolved'
    assert a.emitted==1 and a.raw==3 and a.suppressed==2
def test_unknown_labels_do_not_resolve_quality():
    a=Alerts(C);e=events()
    for x in e:x['probability']=1-x['probability']
    bad=metrics(e,[20]*60,C);a.evaluate(bad,0);a.evaluate(bad,1)
    assert 'quality' in a.active
    unknown=metrics(events(labels=False),[20]*60,C);a.evaluate(unknown,2);a.evaluate(unknown,3)
    assert 'quality' in a.active and unknown['recall'] is None
@pytest.mark.parametrize('n',[0,1,59])
def test_minimum_samples(n):
    a=Alerts(C);m=metrics(events(n,latency=300),[20]*60,C)
    assert a.evaluate(m,0)==[] and a.evaluate(m,1)==[]
def test_drift_identical_and_shifted():
    assert psi([20]*60,[20]*60,C['length_bins'])==0
    assert psi([20]*60,[200]*60,C['length_bins'])>.2
