"""Target-response-free inference using the extracted six-start PSO and features."""
import math,time
from pathlib import Path
import numpy as np,joblib
from threadpoolctl import threadpool_limits
from tools.research_models.target_input_cache import fit_job
from tools.research_models.prefix_budget import response
from tools.research_models.sequential_heuristics import signals,action
from .features import state_vector
from .io import ROOT,FINAL,load,write,table

def normalize(observation,scale):
    value=float(observation['value'])
    if scale['response']=='fraction':return value
    if scale['response']=='removal_percent':return value/100
    if scale['response']=='uptake_mg_g':return value*float(scale['rho_g_L'])/float(scale['C0_mg_L'])
    raise ValueError('response must be fraction, removal_percent or uptake_mg_g')

def predict(payload,model=None,configuration='laboratory_source_excluded'):
    # Input schema deliberately excludes target response/full trajectory. Callers
    # must pass only the currently revealed observations; clocks alone are known.
    allowed={'curve_id','target_time_min','observations','scale','next_time_min','as_of_min'}
    if set(payload)-allowed:raise ValueError('Unknown input fields; target labels/full trajectories are not accepted: '+str(set(payload)-allowed))
    T=float(payload['target_time_min']);obs=payload['observations'];asof=float(payload.get('as_of_min',max(float(p['time_min']) for p in obs)))
    if not math.isfinite(T) or T<=0 or not math.isfinite(asof):raise ValueError('Finite positive target clock and finite as_of_min required')
    times=[float(p['time_min']) for p in obs]
    if len(obs)<3 or any(not math.isfinite(t) or t<=0 or t>=T or t>asof for t in times) or times!=sorted(set(times)):raise ValueError('Need >=3 strictly increasing positive observed times, all <=as_of and <target')
    if payload['scale']['response']=='uptake_mg_g' and (float(payload['scale']['C0_mg_L'])<=0 or float(payload['scale']['rho_g_L'])<=0):raise ValueError('Positive inventory required')
    fractions=[normalize(p,payload['scale']) for p in obs]
    if not all(math.isfinite(x) for x in fractions):raise ValueError('Nonfinite measured response')
    model=joblib.load(ROOT/f'models/{FINAL}/R0_PSO.joblib') if model is None else model
    if configuration=='laboratory_source_excluded':rules=load('data/laboratory/D38_laboratory_config.json')['U0_E_thresholds']
    elif configuration=='common_U0_E':rules={r['method']:r['threshold_pp'] for r in load('reference/uniform_selected_rules.json') if r['case_id']==FINAL and r['scheme']=='U0-E' and r['error_tolerance_pp']==5 and r['deleted_cal_family'] is None}
    elif configuration=='original_frozen':rules={'Learned':next(r['threshold_pp'] for r in load('configs/original_learned_rules.json') if r['case_id']==FINAL and r['method']=='R2_scalar_calibration')}|{r['method']:r['threshold_pp'] for r in load('reference/original_H_rules.json') if r['case_id']==FINAL}
    else:raise ValueError(configuration)
    states=[];parent=None;fits=[];start=time.perf_counter()
    for k in range(3,len(obs)+1):
        inputs=[dict(point_id=f'{payload["curve_id"]}__p{i+1}',time_min=times[i],fraction=fractions[i]) for i in range(k)]
        sid=f'{payload["curve_id"]}__prefix{k}';f=fit_job((sid,sid,inputs));p=f['parameters'];ok=f['available']
        m=dict(available=ok,parameters=p,fe_bound=bool(ok and (p['fe']<=1e-6 or p['fe']>=1-1e-6)),tau_bound=bool(ok and (p['tau_min']<=1.01e-6 or p['tau_min']>=1e6/1.01)))
        s=dict(inputs=inputs,queries=[dict(time_min=T)])
        x=state_vector(s,m,parent);pred=float(response([T],p['fe'],p['tau_min'])[0]) if ok else None
        with threadpool_limits(limits=1):q=float(np.maximum(0,model.predict(np.asarray([x],float)))[0])
        states.append(dict(state_id=sid,k=k,time_min=times[k-1],prediction=pred,available=bool(ok and pred is not None and math.isfinite(pred)),Learned=q if math.isfinite(q) else None,q_pp=q if math.isfinite(q) else None,x=x))
        fits.append(dict(state_id=sid,parameters=p,seconds=f['seconds']));parent=m
    c=dict(curve_id=payload['curve_id'],target_time_min=T,pool=[dict(time_min=t,fraction=y) for t,y in zip(times,fractions)],states=states)
    c['states']=signals(c)
    acts=[action(c,m,rules[m]) for m in rules]
    first=next(a for a in acts if a['method']=='Learned');last=c['states'][-1];scale=payload['scale'];qhat=last['prediction']*float(scale['C0_mg_L'])/float(scale['rho_g_L']) if last['prediction'] is not None and scale['response']=='uptake_mg_g' else None
    return dict(curve_id=c['curve_id'],as_of_min=asof,target_time_min=T,observations_used=len(obs),maximum_observation_time_min=max(times),input_times_min=times,target_response_used=False,normalization=scale,current_prediction_fraction=last['prediction'],current_prediction_mg_g=qhat,current_error_score_pp=last['Learned'],decision='adopt' if first['adopted'] else 'continue',first_adoption=first,next_measurement_min=None if first['adopted'] else payload.get('next_time_min'),threshold_configuration=configuration,thresholds=rules,states=c['states'],fits=fits,decision_seconds=time.perf_counter()-start)

def laboratory(out):
    import csv
    with (ROOT/'data/laboratory/D34_laboratory_raw.csv').open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    results=[];traces=[];actions=[]
    # These payloads physically contain no observations after60. Scoring joins
    # measured endpoints only after every inference result is saved.
    model=joblib.load(ROOT/f'models/{FINAL}/R0_PSO.joblib')
    for cid in sorted({r['series'] for r in raw}):
        pp=[dict(time_min=float(r['t_min']),value=float(r['q_mg_g'])) for r in raw if r['series']==cid and float(r['t_min'])<=60]
        payload=dict(curve_id=cid,target_time_min=120,as_of_min=60,scale=dict(response='uptake_mg_g',C0_mg_L=200,rho_g_L=2),observations=pp,next_time_min=90)
        write(out/f'{cid}_60min_input.json',payload);z=predict(payload,model);write(out/f'{cid}_60min_prediction.json',z);results.append(z)
        # The post-decision90 diagnostic is separate and never fed back to60.
        diag=payload|dict(as_of_min=90,observations=pp+[dict(time_min=90,value=float(next(r['q_mg_g'] for r in raw if r['series']==cid and float(r['t_min'])==90)))],next_time_min=120)
        zz=predict(diag,model)
        traces.extend(dict(series=cid,k=s['k'],time_min=s['time_min'],prediction_mg_g=100*s['prediction'],Learned=s['Learned'],H1=s['H1'],H2=s['H2'],H3=s['H3'],post_decision=s['time_min']>60,PSO_fe=f['parameters']['fe'],tau_min=f['parameters']['tau_min'],prefix_SSE=f['parameters']['training_SSE']) for s,f in zip(zz['states'],zz['fits']))
        for method,threshold in z['thresholds'].items():
            curve=dict(curve_id=cid,states=zz['states']);a=action(curve,method,threshold);state=next((s for s in zz['states'] if s['state_id']==a['selected_state_id']),None)
            actions.append(a|dict(series=cid,stop_time_min=state['time_min'] if state else 120,n_observations=state['k'] if state else 7))
    write(out/'actions_before_truth.json',actions)
    rows=[]
    for z in results:
        truth=float(next(r['q_mg_g'] for r in raw if r['series']==z['curve_id'] and float(r['t_min'])==120))
        rows.append(dict(series=z['curve_id'],prediction_mg_g=z['current_prediction_mg_g'],target_mg_g=truth,error_pp=abs(z['current_prediction_mg_g']-truth),score_pp=z['current_error_score_pp'],decision=z['decision'],observations_used=z['observations_used'],max_input_time_min=z['maximum_observation_time_min'],decision_seconds=z['decision_seconds']))
    table(out/'laboratory_summary.csv',rows);write(out/'laboratory_summary.json',rows);table(out/'laboratory_prefixes.csv',traces);write(out/'laboratory_prefixes.json',traces)
    return rows
