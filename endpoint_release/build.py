"""Build original exhaustive subsets, features and labels from released observations.

The state-ID/mask/parent loop is the original fixed_target120 prepare loop with
I/O adapted; original state_vector/PSO bodies are imported unchanged.
"""
import csv,math,time
from collections import defaultdict
from .io import ROOT,load,write,table,identity
from .features import state_vector
from tools.research_models.prefix_budget import response
from tools.research_models.target_input_cache import fit_job,input_identity

def build(out,recompute_pso=False):
    raw={}
    for ds,name in [('original','original_observations.csv'),('transfer','transfer_observations.csv')]:
        with (ROOT/'data'/name).open(encoding='utf-8-sig') as f:rr=list(csv.DictReader(f))
        for p in rr:raw[ds,p['curve_id'],p['point_id']]=p
    cohort=load('data/admitted_training_cohort.json');cache={r['state_id']:r for r in load('data/pso_parameter_cache.json')};roles={c['curve_id']:c for c in load('reference/original_scores/original_fit_cal_to_transfer.json')}
    # Canonical labels for every original curve are explicitly recorded in folds.
    membership={}
    with (ROOT/'data/group_membership.csv').open(encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):membership[r['curve_id']]=r['canonical_group_id']
    rows=[];states=[];models={};differences=[];nnew=0;started=time.perf_counter();recipe=load('configs/pso_recipe.json')
    for c in cohort:
        cid=c['curve_id'];pool=c['pool_points'];q=c['target_point'];ds=c['dataset'];by_mask={}
        # Target and input membership must equal time-only admission, not a
        # response-based endpoint/maximum selection.
        allp=[p for (d,i,_),p in raw.items() if d==ds and i==cid]
        lo='time_lower' if ds=='original' else 'time_lower_min';hi='time_upper' if ds=='original' else 'time_upper_min'
        tt=[p for p in allp if p.get(lo) and p.get(hi) and float(p[lo])<=120<=float(p[hi])]
        assert len(tt)==1 and tt[0]['point_id']==q['point_id']
        admitted=sorted([p for p in allp if float(p['time_min'])>0 and p.get(hi) and float(p[hi])<q['time_lower']],key=lambda p:(float(p['time_min']),p['point_id']))
        assert [p['point_id'] for p in admitted]==[p['point_id'] for p in pool]
        target=float(raw[ds,cid,q['point_id']]['fraction'])
        for mask in range(1<<(len(pool)-3)):
            ii=[0,1,2]+[3+j for j in range(len(pool)-3) if mask&(1<<j)]
            ins=[dict(point_id=pool[i]['point_id'],time_min=pool[i]['time_min'],fraction=float(raw[ds,cid,pool[i]['point_id']]['fraction'])) for i in ii]
            sid=identity(dict(task='nominal120',curve_id=cid,input_ids=[p['point_id'] for p in ins],query_id=q['point_id'],query_time=q['time_min']))[:24]
            by_mask[mask]=sid;parent=by_mask[mask^(1<<(mask.bit_length()-1))] if mask else None
            s=dict(state_id=sid,curve_id=cid,n=len(ins),inputs=ins,queries=[dict(point_id=q['point_id'],time_min=q['time_min'])])
            if recompute_pso:
                ff=fit_job((sid,sid,ins));p=ff['parameters'];ok=ff['available'];nnew+=1
                m=dict(state_id=sid,parameters=p,available=ok,fe_bound=bool(ok and(p['fe']<=1e-6 or p['fe']>=1-1e-6)),tau_bound=bool(ok and(p['tau_min']<=1.01e-6 or p['tau_min']>=1e6/1.01)))
            else:
                if sid not in cache:raise ValueError('Explicit released PSO cache missing state '+sid+'; use --recompute-pso')
                m=cache[sid]
                actual_key=input_identity(cid,ins,recipe['optimizer'],recipe['fit_code_sha256'])
                if actual_key!=m['fit_key']:raise ValueError('PSO cache input/value/time/recipe identity mismatch: '+sid+'; use --recompute-pso')
            models[sid]=m;x=state_vector(s,m,models.get(parent));states.append(s|dict(mask=mask,parent_state_id=parent,x=x))
            if ds=='original' and m['available']:
                pred=float(response([q['time_min']],m['parameters']['fe'],m['parameters']['tau_min'])[0]);loss=100*abs(pred-target)
                rows.append(dict(row_id=sid,curve_id=cid,doi=c['doi'],family=membership[cid],recorded_family=c['family'],n=len(ins),loss_pp=loss,x=x))
    reference=load('reference/training_dataset.json');assert [r['row_id'] for r in rows]==[r['row_id'] for r in reference]
    maxx=max(abs(a-b) for r,z in zip(rows,reference) for a,b in zip(r['x'],z['x']));maxy=max(abs(r['loss_pp']-z['loss_pp']) for r,z in zip(rows,reference))
    if not recompute_pso:assert maxx<1e-12 and maxy<1e-10
    write(out/'training_dataset.json',rows);write(out/'rebuilt_states.json',states)
    receipt=dict(states=len(states),training_rows=len(rows),full_prefix_and_nonconsecutive_subsets=True,subsets='first3 fixed, exhaustive subsets of all remaining strictly pretarget points; no sampling/cap/seed',new_pso_fits=nnew,explicit_cache_hits=0 if recompute_pso else len(states),max_feature_difference=maxx,max_label_difference_pp=maxy,seconds=time.perf_counter()-started)
    write(out/'build_receipt.json',receipt);print('BUILT',receipt,flush=True);return rows
