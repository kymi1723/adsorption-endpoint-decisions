"""Fixed clock plans, source-weighted calibration and frozen mean-cost arithmetic.

Plan selection reads clocks alone. No alternative state is sought after a
planned PSO failure. Labels enter calibration/scoring, never test plan choice.
"""
import math
from collections import Counter
from fractions import Fraction as F
from tools.research_models.source_sequential_acceptance import summarize,feasible

METHODS=['R0','F_PSO','F_Last','R2']
SIMPLE_PRIORITY={'R0':0,'F_Last':1,'F_PSO':2}

def fixed_state(curve,r):
    if r is None:return None
    return next((s for s in curve['states'] if s['k']>=3 and s['time_min']<curve['target_time_min'] and s['time_min']/curve['target_time_min']>=r),None)

def fixed_action(curve,r,predictor):
    state=fixed_state(curve,r)
    if state is not None:
        value=state['prediction'] if predictor=='PSO' else state['last_fraction']
        if (predictor=='PSO' and not state['available']) or value is None or not math.isfinite(value):state=None
    return dict(curve_id=curve['curve_id'],selected_state_id=state['state_id'] if state else None,prediction=(state['prediction'] if predictor=='PSO' else state['last_fraction']) if state else None,adopted=state is not None,planned_ratio=r,predictor=predictor)

def score_action(curve,action,target_fraction):
    state=next((s for s in curve['states'] if s['state_id']==action['selected_state_id']),None) if action['selected_state_id'] is not None else None
    adopted=state is not None
    assert adopted==action['adopted']
    pred=action['prediction'] if adopted else target_fraction
    error=100*abs(pred-target_fraction) if adopted else 0.
    n=state['k'] if adopted else curve['pool_count']+1;t=state['time_min'] if adopted else curve['target_time_min']
    return {k:curve[k] for k in ['dataset','curve_id','source_id','doi','family','canonical_group_id']}|dict(state_id=state['state_id'] if adopted else None,selected_k=state['k'] if adopted else None,adopted=adopted,wrong_adoption=adopted and error>5.,prediction=pred,target_fraction=target_fraction,absolute_error_pp=error,adoption_time_min=t,elapsed_time_min=t,t3_min=curve['t3'],wait_min=t-curve['t3'],target_time_min=curve['target_time_min'],time_over_target=t/curve['target_time_min'],new_measurements=n-3,n_observations=n,target_fallback=not adopted)

def summary(rows):
    z=summarize(rows)
    z['conditional_MAE_pp']=z['absolute_error_pp']/z['A'] if z['A'] else None
    adopted=[r for r in rows if r['adopted']]
    z['curve_equal_conditional_MAE_pp']=math.fsum(r['absolute_error_pp'] for r in adopted)/len(adopted) if adopted else None
    return z

def source_mean(rows,key):
    counts=Counter(r['canonical_group_id'] for r in rows)
    return math.fsum(r[key]/(len(counts)*counts[r['canonical_group_id']]) for r in rows)

def mean_cost(error_pp,n_observations,stop_time_min,t3_min,lambda_pp,mu_pp_per_min):
    return error_pp+lambda_pp*(n_observations-3)+mu_pp_per_min*(stop_time_min-t3_min)

def with_cost(row,lam,mu):
    return row|dict(lambda_pp=lam,mu_pp_per_min=mu,J_pp=mean_cost(row['absolute_error_pp'],row['n_observations'],row['adoption_time_min'],row['t3_min'],lam,mu))

def calibrate_fixed(curves,targets,predictor):
    candidates=sorted({0.,1.}|{s['time_min']/c['target_time_min'] for c in curves for s in c['states'] if s['k']>=3 and s['time_min']<c['target_time_min']})
    trace=[];best=None
    for ordinal,r in enumerate(candidates):
        rows=[score_action(c,fixed_action(c,r,predictor),targets[c['curve_id']]) for c in curves];z=summary(rows)
        rr=dict(candidate_ordinal=ordinal,r=r,feasible=feasible(z),**z);trace.append(rr)
        if rr['feasible']:
            rank=(-F(z['A_exact']),z['wait_min'],r)
            if best is None or rank<best[0]:best=rank,rr
    return dict(r=best[1]['r'] if best else 1.,status='calibrated_fixed_time' if best else 'no_feasible_fixed_time_rule',chosen_candidate_ordinal=best[1]['candidate_ordinal'] if best else candidates.index(1.)),trace

def select_simple(calibration_results,lam,mu):
    values={method:source_mean([with_cost(r,lam,mu) for r in rows],'J_pp') for method,rows in calibration_results.items()}
    chosen=min(values,key=lambda method:(values[method],SIMPLE_PRIORITY[method]))
    return chosen,values
