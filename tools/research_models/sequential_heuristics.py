"""Three frozen prefix-only stopping signals and source-equal calibration.

No fitting or estimator loading. Targets enter evaluate/calibrate only.
Threshold endpoints are JSON-safe strings; all comparisons use numeric values.
"""
import math
from fractions import Fraction
import numpy as np
from tools.research_models.fixed_time_acceptance import score_action, summary

METHODS = ('H1', 'H2', 'H3')


def signals(curve):
    previous = None
    result = []
    for s in curve['states']:
        points = curve['pool'][:s['k']]
        recent = points[-3:]
        values = [p['fraction'] for p in recent]
        dt = recent[-1]['time_min'] - recent[0]['time_min']
        h1 = 100 * (max(values)-min(values)) * (curve['target_time_min']-s['time_min'])/dt if dt > 0 else None
        parent_ok = s['k'] >= 4 and previous is not None and previous['k'] == s['k']-1 and previous['available']
        h2 = 100*abs(s['prediction']-previous['prediction']) if parent_ok and s['available'] else None
        x = s['x']
        h3 = math.expm1(x[18]) if parent_ok and x[19] == 1 else None
        result.append(s | dict(H1=h1, H2=h2, H3=h3))
        previous = s
    return result


def numeric_threshold(value):
    return {'-inf': -math.inf, '+inf': math.inf}.get(value, value) if isinstance(value, str) else value


def candidate_thresholds(curves, method):
    values = [s[method] for c in curves for s in c['states'] if s[method] is not None and math.isfinite(s[method])]
    finite = sorted(set(float(x) for x in np.quantile(values, np.arange(41)/40, method='linear'))) if values else []
    return ['-inf'] + finite + ['+inf']


def action(curve, method, threshold):
    t = numeric_threshold(threshold)
    state = next((s for s in curve['states'] if s['available'] and s['prediction'] is not None and math.isfinite(s['prediction']) and s[method] is not None and math.isfinite(s[method]) and s[method] <= t), None)
    return dict(curve_id=curve['curve_id'], method=method, threshold_pp=threshold,
                selected_state_id=state['state_id'] if state else None,
                prediction=state['prediction'] if state else None, adopted=state is not None,
                signal_pp=state[method] if state else None)


def evaluate(curves, targets, method, threshold):
    return [score_action(c, action(c, method, threshold), targets[c['curve_id']]) | dict(method=method) for c in curves]


def eligible(row):
    return Fraction(row['A_exact']) > 0 and row['R_exact'] is not None and Fraction(row['R_exact']) <= Fraction(1,20)


def rank(row):
    return (-Fraction(row['A_exact']), row['wait_min'], row['n_observations'], numeric_threshold(row['threshold_pp']))


def calibrate(curves, targets, method, candidates):
    trace=[]
    for i, t in enumerate(candidates):
        z=summary(evaluate(curves, targets, method, t))
        trace.append(dict(candidate_ordinal=i, threshold_pp=t, feasible=eligible(z), **z))
    feasible=[r for r in trace if r['feasible']]
    chosen=min(feasible,key=rank) if feasible else trace[0]
    return dict(method=method, threshold_pp=chosen['threshold_pp'], chosen_candidate_ordinal=chosen['candidate_ordinal'], status='feasible_adoption' if feasible else 'all_fallback', calibration_summary=chosen), trace
