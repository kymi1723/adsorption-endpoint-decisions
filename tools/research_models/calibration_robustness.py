"""Finite threshold sensitivity from cached scores, with exact family weighting.

No estimator imports, no fitting, no feature/signal recomputation. Quantile
calibration reuses equivalent exhaustive cutpoints; test uses actual thresholds.
"""
import math,bisect
from fractions import Fraction as F
import numpy as np
from tools.research_models.sequential_heuristics import action,numeric_threshold
from tools.research_models.fixed_time_acceptance import score_action,summary

def thresholds(curves,method,kind='E'):
    values=[s[method] for c in curves for s in c['states'] if s.get(method) is not None and math.isfinite(s[method])]
    finite=sorted(set(float(v) for v in values))
    if kind=='Q':finite=sorted(set(float(v) for v in np.quantile(values,np.arange(41)/40,method='linear'))) if values else []
    return ['-inf']+finite+['+inf']

def score(curve,a,target,tolerance):
    r=score_action(curve,a,target)
    r['wrong_adoption']=bool(r['adopted'] and r['absolute_error_pp']>tolerance)
    return r

def trace(curves,targets,method,tolerance):
    rows=[]
    for i,t in enumerate(thresholds(curves,method,'E')):
        metrics=summary([score(c,action(c,method,t),targets[c['curve_id']],tolerance) for c in curves])
        rows.append(dict(candidate_ordinal=i,threshold_pp=t,**metrics))
    return rows

def quantile_trace(curves,method,exact):
    cutpoints=[numeric_threshold(r['threshold_pp']) for r in exact];rows=[]
    for i,t in enumerate(thresholds(curves,method,'Q')):
        index=bisect.bisect_right(cutpoints,numeric_threshold(t))-1
        rows.append(exact[index]|dict(candidate_ordinal=i,threshold_pp=t,equivalent_E_ordinal=index))
    return rows

def feasible(r,minimum):
    A=F(r['A_exact']);return A>0 and A>=F(minimum) and r['R_exact'] is not None and F(r['R_exact'])<=F(1,20)

def choose(rows,minimum=0):
    valid=[r for r in rows if feasible(r,minimum)]
    winner=min(valid,key=lambda r:(-F(r['A_exact']),r['wait_min'],r['n_observations'],numeric_threshold(r['threshold_pp']))) if valid else rows[0]
    return dict(threshold_pp=winner['threshold_pp'],status='adoption_feasible' if valid else 'all_fallback',chosen_candidate_ordinal=winner['candidate_ordinal'],calibration_summary=winner)

def family_metrics(rows):
    result=[]
    for g in sorted({r['canonical_group_id'] for r in rows}):
        rr=[r for r in rows if r['canonical_group_id']==g];z=summary(rr)
        result.append(dict(canonical_group_id=g,**z))
    return result

def cluster_replicates(family_rows,draws):
    keys=['A','B','wait_min','n_observations'];arr=np.array([[r[k] for k in keys] for r in family_rows],float)
    means=arr[draws].mean(axis=1);R=np.divide(means[:,1],means[:,0],out=np.full(len(draws),np.nan),where=means[:,0]>0)
    return dict(A=means[:,0],B=means[:,1],R=R,wait_min=means[:,2],n_observations=means[:,3])

def descriptive(values):
    finite=np.asarray(values,float);ok=np.isfinite(finite);v=finite[ok]
    qs=np.quantile(v,[.025,.5,.975],method='linear') if len(v) else [None]*3
    return dict(lower=float(qs[0]) if qs[0] is not None else None,median=float(qs[1]) if qs[1] is not None else None,upper=float(qs[2]) if qs[2] is not None else None,undefined_fraction=float(1-ok.mean()),valid_replicates=int(ok.sum()),degenerate=bool(len(v) and np.max(v)==np.min(v)))
