"""Recompute learned scores, calibration and first actions; truth joins last."""
from collections import defaultdict
from pathlib import Path
import math,time
import numpy as np,joblib
from .io import ROOT,FINAL,METHODS,load,read,write,table
from tools.research_models.sequential_heuristics import signals,action,candidate_thresholds,calibrate
from tools.research_models.calibration_robustness import trace,choose,score
from tools.research_models.source_sequential_acceptance import calibrate_scalar
from tools.research_models.fixed_time_acceptance import summary

def score_bank(model_dir):
    bases={c['curve_id']:c for c in load('data/evaluation_curves.json')};folds=load('configs/folds.json');bank={};maxdiff=0.
    old=load('reference/case_curve_score_bank.json')
    for f in folds:
        case=f['case_id'];head=joblib.load(Path(model_dir)/case/'R0_PSO.joblib');bank[case]={}
        ids=f['calibration_curve_ids']+f['test_curve_ids']
        if case==FINAL:ids+= [cid for cid,c in bases.items() if c['batch_id'] not in ['original79','transfer19']]
        for cid in ids:
            c=bases[cid];raw=np.maximum(0,head.predict(np.asarray([s['x'] for s in c['states']],float)))
            states=[s|dict(Learned=float(v) if math.isfinite(v) else None,q_pp=float(v) if math.isfinite(v) else None) for s,v in zip(signals(c),raw)]
            bank[case][cid]=c|dict(states=states)
            for s,o in zip(states,old[case][cid]['states']):
                assert s['state_id']==o['state_id']
                if s['Learned'] is not None and o['Learned'] is not None:maxdiff=max(maxdiff,abs(s['Learned']-o['Learned']))
    return bank,maxdiff

def evaluate(out,scheme='U0-E',model_dir=None,bank=None):
    model_dir=Path(model_dir or ROOT/'models')
    if bank is None:bank,score_difference=score_bank(model_dir)
    else:score_difference=None
    folds=load('configs/folds.json');labels=load('data/calibration_targets.json');rules=[];candidates=[];actions=[];timings=[]
    for f in folds:
        case=f['case_id'];cal=[bank[case][cid] for cid in f['calibration_curve_ids']]
        for method in METHODS:
            start=time.perf_counter()
            if scheme=='U0-E':
                rows=trace(cal,labels,method,5);rule=choose(rows,0)
            elif scheme=='Original_frozen' and method=='Learned':
                cc=[c|dict(target_fraction=labels[c['curve_id']],states=[s|dict(q_pp=s['Learned']) for s in c['states']]) for c in cal]
                rule,rows=calibrate_scalar(cc)
            elif scheme=='Original_frozen':rule,rows=calibrate(cal,labels,method,candidate_thresholds(cal,method))
            else:raise ValueError(scheme)
            timings.append(dict(case_id=case,method=method,scheme=scheme,candidates=len(rows),calibration_seconds=time.perf_counter()-start,scope='candidate generation, full calibration first-action replays and selection; excludes model loading/scoring'))
            rules.append(rule|dict(case_id=case,method=method,scheme=scheme));candidates.extend(r|dict(case_id=case,method=method) for r in rows)
            ids=f['test_curve_ids']
            if case==FINAL:ids=ids+[cid for cid,c in bank[case].items() if c['batch_id'] not in ['original79','transfer19']]
            threshold=rule['threshold_pp']
            for cid in ids:
                c=bank[case][cid]
                a=action(c,method,'-inf' if threshold is None else threshold)
                actions.append(a|dict(case_id=case,batch_id=c['batch_id'],scheme=scheme))
    write(out/'selected_rules.json',rules);write(out/'calibration_candidates.json',candidates);write(out/'actions_before_truth.json',actions);table(out/'calibration_timings.csv',timings);write(out/'calibration_timings.json',timings)
    targets=load('data/test_targets.json');rows=[]
    for a in actions:
        c=bank[a['case_id']][a['curve_id']];rows.append(score(c,a,targets[c['curve_id']],5)|dict(case_id=a['case_id'],batch_id=c['batch_id'],method=a['method'],scheme=scheme))
    groups=defaultdict(list)
    for r in rows:groups[r['batch_id'],r['method']].append(r)
    metrics=[dict(batch_id=b,method=m,scheme=scheme,**summary(rr)) for (b,m),rr in groups.items()]
    costs=[];wins=[]
    for r in metrics:
        for lam in [0,.5,1,2,5]:
            for mu in [0,.025,.05,.1]:costs.append({k:r[k] for k in ['batch_id','method','scheme']}|dict(lambda_pp=lam,mu_pp_min=mu,scenario_weighted_loss=r['absolute_error_pp']+lam*(r['n_observations']-3)+mu*r['wait_min']))
    for batch in dict.fromkeys(r['batch_id'] for r in metrics):
        for method in ['H1','H2','H3']:
            delta=[]
            for lam in [0,.5,1,2,5]:
                for mu in [0,.025,.05,.1]:
                    get=lambda m:next(r['scenario_weighted_loss'] for r in costs if r['batch_id']==batch and r['method']==m and r['lambda_pp']==lam and r['mu_pp_min']==mu)
                    delta.append(get('Learned')-get(method))
            wins.append(dict(batch_id=batch,comparison='Learned-'+method,scheme=scheme,lower_cells=sum(v<-1e-10 for v in delta),equal_cells=sum(abs(v)<=1e-10 for v in delta),mean20_delta_loss=math.fsum(delta)/20))
    for name,obj in [('curve_results',rows),('policy_layer_metrics',metrics),('scenario20',costs),('scenario_wins',wins)]:write(out/(name+'.json'),obj);table(out/(name+'.csv'),obj)
    receipt=dict(scheme=scheme,model_count=len(folds),evaluated_curves=len(rows)//4,action_rows=len(actions),fresh_model_score_max_difference_pp=score_difference,model_directory='frozen release models' if model_dir==ROOT/'models' else 'separate retraining output',test_responses_used_for_threshold_selection=False,training_runs=0)
    write(out/'evaluation_receipt.json',receipt)
    from .comparators import replay_fixed
    replay_fixed(out)
    print('EVALUATED',receipt,flush=True);print([(r['batch_id'],r['method'],r['adopted_count']) for r in metrics if r['batch_id'] in ['original79','transfer19'] and r['method'] in ['Learned','H1']],flush=True)
    return metrics,wins
