"""Replay recorded fixed-clock/target comparators without changing calibration."""
from collections import defaultdict
from .io import FINAL,load,write,table
from tools.research_models.fixed_time_acceptance import fixed_action,score_action,summary,source_mean

def replay_fixed(out):
    curves={r['curve_id']:r for r in load('data/evaluation_curves.json')};folds=load('configs/folds.json');rules=load('configs/fixed_time_rules.json');actions=[];rows=[];visible={}
    for f in folds:
        case=f['case_id'];ids=f['test_curve_ids']
        if case==FINAL:ids=ids+[cid for cid,c in curves.items() if c['batch_id'] not in ['original79','transfer19']]
        for cid in ids:
            c=curves[cid];c=c|dict(states=[s|dict(last_fraction=c['pool'][s['k']-1]['fraction']) for s in c['states']])
            visible[cid]=c
            for method in ['R0','F_PSO','F_Last']:
                if method=='R0':a=dict(curve_id=cid,selected_state_id=None,prediction=None,adopted=False)
                else:
                    rule=next(r for r in rules if r['case_id']==case and r['method']==method);a=fixed_action(c,rule['r'],rule['predictor'])
                actions.append(a|dict(method=method,case_id=case,batch_id=c['batch_id']))
    write(out/'fixed_time_actions_before_truth.json',actions)
    targets=load('data/test_targets.json')
    for a in actions:
        c=visible[a['curve_id']];rows.append(score_action(c,a,targets[c['curve_id']])|dict(method=a['method'],case_id=a['case_id'],batch_id=c['batch_id'],configuration='recorded_original_fixed_time'))
    ref={(r['curve_id'],r['method']):r for r in load('reference/original_baseline_curve_results.json') if r['method'] in ['R0','F_PSO','F_Last']}
    for r in rows:
        o=ref[r['curve_id'],r['method']]
        for k in ['adopted','state_id','n_observations','adoption_time_min']:assert r[k]==o[k],(r['curve_id'],r['method'],k)
        assert abs(r['absolute_error_pp']-o['absolute_error_pp'])<1e-10
    groups=defaultdict(list)
    for r in rows:groups[r['batch_id'],r['method']].append(r)
    metrics=[dict(batch_id=b,method=m,configuration='recorded_original_fixed_time',**summary(rr)) for (b,m),rr in groups.items()]
    write(out/'fixed_time_results.json',rows);write(out/'fixed_time_metrics.json',metrics);table(out/'fixed_time_metrics.csv',metrics)
    write(out/'fixed_time_replay_receipt.json',dict(passed=True,action_rows=len(rows),original_first_actions_exact=True,threshold_reselection=False,configuration='recorded original fixed-time; never claimed to be U0-E recalibration'))
    choices=load('configs/simple_cal_choices.json');by={(r['curve_id'],r['method']):r for r in rows};simple=[]
    for f in folds:
        case=f['case_id'];ids=f['test_curve_ids']
        if case==FINAL:ids=ids+[cid for cid,c in curves.items() if c['batch_id'] not in ['original79','transfer19']]
        for choice in [q for q in choices if q['case_id']==case]:
            for cid in ids:
                r=by[cid,choice['selected_method']];lam=choice['lambda_pp'];mu=choice['mu_pp_per_min'];simple.append(r|dict(method='Simple_cal',selected_method=choice['selected_method'],lambda_pp=lam,mu_pp_per_min=mu,J_pp=r['absolute_error_pp']+lam*(r['n_observations']-3)+mu*r['wait_min']))
    cells=defaultdict(list)
    for r in simple:cells[r['batch_id'],r['lambda_pp'],r['mu_pp_per_min']].append(r)
    costs=[dict(batch_id=b,lambda_pp=lam,mu_pp_per_min=mu,source_equal_loss_pp=source_mean(rr,'J_pp')) for (b,lam,mu),rr in cells.items()]
    write(out/'Simple_cal_curve_costs.json',simple);table(out/'Simple_cal_scenario20.csv',costs);write(out/'Simple_cal_scenario20.json',costs)
    return rows
