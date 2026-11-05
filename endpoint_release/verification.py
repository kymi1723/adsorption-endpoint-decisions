"""One meaningful frozen/model-interface acceptance run; no training/search."""
import csv,math,time,sys,platform,importlib.metadata as md
import numpy as np
from .io import ROOT,FINAL,load,write,table,read
from .evaluation import evaluate,score_bank
from .inference import laboratory,predict

def verify(out):
    bank,maxdiff=score_bank(ROOT/'models');assert maxdiff<1e-10
    mdir=out/'U0-E';mdir.mkdir();metrics,wins=evaluate(mdir,'U0-E',bank=bank)
    expected={('original79','Learned'):60,('original79','H1'):39,('transfer19','Learned'):15,('transfer19','H1'):5}
    for (batch,method),n in expected.items():assert next(r['adopted_count'] for r in metrics if r['batch_id']==batch and r['method']==method)==n
    for batch,n in [('original79',17),('transfer19',16)]:assert next(r['lower_cells'] for r in wins if r['batch_id']==batch and r['comparison']=='Learned-H1')==n
    # Compare all U0-E layer metrics with saved, not just headline adoption.
    reference=[r for r in load('reference/paper_tables/T01_policy_layer_metrics.json') if r['scheme']=='U0-E' and r['error_tolerance_pp']==5 and r['deleted_cal_family'] is None]
    diffs=[]
    for r in metrics:
        o=next(q for q in reference if q['batch_id']==r['batch_id'] and q['method']==r['method'])
        for k in ['A_exact','B_exact','R_exact','adopted_count','wrong_adoption_count']:assert r[k]==o[k],(r['batch_id'],r['method'],k,r[k],o[k])
        for k in ['absolute_error_pp','wait_min','n_observations','conditional_MAE_pp']:
            if r[k] is None or o[k] is None:assert r[k] is o[k]
            else:diffs.append(abs(r[k]-o[k]))
    assert max(diffs)<1e-10
    orig=out/'Original_frozen';orig.mkdir();evaluate(orig,'Original_frozen',bank=bank)
    lab=out/'laboratory';lab.mkdir();rr=laboratory(lab)
    expected_p=[95.4497,92.8055,93.9500];expected_e=[.1097,1.4745,.8400]
    for r,p,e in zip(rr,expected_p,expected_e):
        assert abs(r['prediction_mg_g']-p)<.0001 and abs(r['error_pp']-e)<.0001
        assert r['observations_used']==5 and r['max_input_time_min']==60 and r['decision']=='adopt'
        payload=read(lab/(r['series']+'_60min_input.json'))
        # Negative leakage probe: even if supplied, a90min point is rejected
        # for the60min call before any new fit/prediction is run.
        bad=payload|dict(observations=payload['observations']+[dict(time_min=90,value=0)])
        try:predict(bad)
        except ValueError:pass
        else:raise AssertionError('Future input not rejected')
    # Single complete online call, cold head load included. This is one timed
    # deployment query, distinct from historical timing or batch amortization.
    payload=read(lab/'parallel_1_60min_input.json');start=time.perf_counter();z=predict(payload);total=time.perf_counter()-start
    write(out/'decision_timing.json',dict(curve='parallel_1',as_of_min=60,observed_points=5,target_min=120,complete_decision_seconds=total,prefix_fit_feature_score_seconds=z['decision_seconds'],includes='joblib load, PSO for n3/n4/n5, features, tree scores, first decision',excludes='interpreter import/startup, physical experiment, plotting, endpoint truth',repeat_count=1))
    receipts=dict(passed=True,frozen_score_max_difference_pp=maxdiff,uniform_metric_max_difference=max(diffs),adoption_counts_verified=True,scenario_wins={'original79':17,'transfer19':16},laboratory_three_series=rr,all_60min_calls_observe_only_times=[5,10,20,30,60],future90min_payload_rejected=True,python=sys.version,platform=platform.platform(),versions={n:md.version(n) for n in ['numpy','scipy','scikit-learn','joblib','matplotlib','threadpoolctl','pillow']},retraining_status='separate train --all-cases run; see independent training_receipt and prediction_consistency')
    write(out/'verification_receipt.json',receipts);print('FROZEN_VERIFICATION_PASSED',rr,flush=True)
