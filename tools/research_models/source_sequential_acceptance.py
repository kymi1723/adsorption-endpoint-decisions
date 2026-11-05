"""Source-weighted first-adoption calibration on a fixed complete-prefix path.

Scores are error regressions (pp), not probabilities. Labels are only used by
calibration/metrics; choose_state uses visible score/time/availability alone.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
import math

def choose_state(curve,threshold=None,allowed=None):
    if threshold is None:return None
    for s in curve['states']:
        q=s['q_pp']
        if s['available'] and q is not None and math.isfinite(q) and q<=threshold and (allowed is None or s['k'] in allowed):return s
    return None

def replay(curves,threshold=None,allowed=None):
    records=[]
    for c in curves:
        s=choose_state(c,threshold,allowed);adopt=s is not None
        err=100*abs(s['prediction']-c['target_fraction']) if adopt else 0.
        n=s['k'] if adopt else c['pool_count']+1
        t=s['time_min'] if adopt else c['target_time_min']
        records.append(dict(dataset=c['dataset'],curve_id=c['curve_id'],source_id=c['source_id'],doi=c['doi'],family=c['family'],canonical_group_id=c['canonical_group_id'],state_id=s['state_id'] if adopt else None,adopted=adopt,wrong_adoption=adopt and err>5.,absolute_error_pp=err,prediction=s['prediction'] if adopt else c['target_fraction'],target_fraction=c['target_fraction'],target_time_min=c['target_time_min'],adoption_time_min=t,time_over_target=t/c['target_time_min'],n_observations=n,new_measurements=n-3,wait_min=t-c['t3'],elapsed_time_min=t,target_fallback=not adopt,q_pp=s['q_pp'] if adopt else None,selected_k=s['k'] if adopt else None))
    return records

def summarize(records):
    counts=Counter(r['canonical_group_id'] for r in records);K=len(counts)
    if not K:raise ValueError('Empty population must be reported, never silently scored')
    w=[F(1,K*counts[r['canonical_group_id']]) for r in records]
    A=sum((a for a,r in zip(w,records) if r['adopted']),F());B=sum((a for a,r in zip(w,records) if r['wrong_adoption']),F())
    R=B/A if A else None
    return dict(groups=K,curves=len(records),A=float(A),B=float(B),R=float(R) if R is not None else None,A_exact=str(A),B_exact=str(B),R_exact=str(R) if R is not None else None,adopted_count=sum(r['adopted'] for r in records),wrong_adoption_count=sum(r['wrong_adoption'] for r in records),curve_equal_A=sum(r['adopted'] for r in records)/len(records),curve_equal_B=sum(r['wrong_adoption'] for r in records)/len(records),curve_equal_R=sum(r['wrong_adoption'] for r in records)/sum(r['adopted'] for r in records) if any(r['adopted'] for r in records) else None,**{k:math.fsum(float(a)*r[k] for a,r in zip(w,records)) for k in ['absolute_error_pp','wait_min','elapsed_time_min','new_measurements','n_observations','target_fallback']})

def feasible(s):return s['R_exact'] is not None and F(s['R_exact'])<=F(1,20) and F(s['A_exact'])>=F(1,4)

def calibrate_scalar(curves):
    candidates=sorted({5.}|{s['q_pp'] for c in curves for s in c['states'] if s['q_pp'] is not None and math.isfinite(s['q_pp']) and 0<=s['q_pp']<=5})
    trace=[];best=None
    for ordinal,c in enumerate(candidates):
        summary=summarize(replay(curves,c));row=dict(candidate_ordinal=ordinal,threshold_pp=c,all_reject=False,feasible=feasible(summary),**summary);trace.append(row)
        if row['feasible']:
            key=(-F(row['A_exact']),row['wait_min'],c)
            if best is None or key<best[0]:best=key,row
    trace.append(dict(candidate_ordinal=len(trace),threshold_pp=None,all_reject=True,feasible=False,**summarize(replay(curves))))
    return dict(threshold_pp=best[1]['threshold_pp'] if best else None,allowed_k=None,status='calibrated_scalar' if best else 'no_feasible_scalar_rule',chosen_candidate_ordinal=best[1]['candidate_ordinal'] if best else len(trace)-1),trace

def calibrate_mask(curves):
    stages=sorted({s['k'] for c in curves for s in c['states']});initial=[];allowed=[]
    # Retain all source curves in every denominator, even when that stage is absent.
    for k in stages:
        rows=[]
        for c in curves:
            s=next((s for s in c['states'] if s['k']==k),None)
            a=bool(s and s['available'] and s['q_pp'] is not None and math.isfinite(s['q_pp']) and s['q_pp']<=5)
            rows.append(dict(canonical_group_id=c['canonical_group_id'],adopted=a,wrong_adoption=bool(a and 100*abs(s['prediction']-c['target_fraction'])>5),absolute_error_pp=0.,wait_min=0.,elapsed_time_min=0.,new_measurements=0,n_observations=0,target_fallback=False))
        z=summarize(rows);ok=z['R_exact'] is not None and F(z['R_exact'])<=F(1,20)
        initial.append(dict(k=k,allowed=ok,**z))
        if ok:allowed.append(k)
    trace=[]
    while allowed:
        z=summarize(replay(curves,5.,set(allowed)));trace.append(dict(step=len(trace),allowed_k=allowed.copy(),**z))
        if z['R_exact'] is not None and F(z['R_exact'])<=F(1,20):
            if F(z['A_exact'])>=F(1,4):return dict(threshold_pp=5.,allowed_k=allowed.copy(),status='calibrated_stage_mask'),initial,trace
            return dict(threshold_pp=None,allowed_k=[],status='insufficient_coverage_mask'),initial,trace
        allowed=allowed[1:]
    trace.append(dict(step=len(trace),allowed_k=[],**summarize(replay(curves))))
    return dict(threshold_pp=None,allowed_k=[],status='no_feasible_mask_rule'),initial,trace

def dependency_closure(rows,preferred_families):
    """Use only recorded equality/alias edges; never infer teams from names."""
    parent={};edges=[]
    def find(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):
        x,y=find(a),find(b)
        if x!=y:parent[max(x,y)]=min(x,y)
    for r in rows:
        values=[]
        for k in ['family','recorded_family','analysis_family','recorded_family_id','analysis_family_id']:
            if r.get(k):values.append(('family',r[k]))
        for k in ['curve_id','source_id','doi']:
            if r.get(k):values.append((k,r[k].strip().lower() if k=='doi' else r[k]))
        nodes=[kind+':'+value for kind,value in dict.fromkeys(values)]
        for node in nodes[1:]:union(nodes[0],node);edges.append(dict(left=nodes[0],right=node,basis=r.get('_basis','recorded metadata equality/alias')))
    components=defaultdict(list)
    for node in parent:components[find(node)].append(node)
    mapping={};detail=[]
    for root,nodes in sorted(components.items()):
        families=sorted(x[7:] for x in nodes if x.startswith('family:'));preferred=sorted(set(families)&set(preferred_families))
        if not families:continue
        canonical=(preferred or families)[0]
        for fam in families:mapping[fam]=canonical
        detail.append(dict(canonical_group_id=canonical,recorded_family_labels=families,source_ids=sorted(x[10:] for x in nodes if x.startswith('source_id:')),dois=sorted(x[4:] for x in nodes if x.startswith('doi:'))))
    return mapping,detail,edges
