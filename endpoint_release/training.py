"""Original weighted tree fitting recipe, with separate outputs and timing."""
from pathlib import Path
import time,math
import numpy as np,joblib
from sklearn.ensemble import ExtraTreesRegressor
from threadpoolctl import threadpool_limits
from .io import ROOT,FINAL,load,read,write,table
from .weights import hierarchy_weights
from .build import build
from .evaluation import evaluate,score_bank

def train(out,all_cases=False,recompute_pso=False):
    dataout=out/'build';dataout.mkdir();rows=build(dataout,recompute_pso)
    recipe=load('configs/training_recipe.json');folds=load('configs/folds.json');timings=[];comparison=[]
    active=folds if all_cases else [f for f in folds if f['case_id']==FINAL]
    # In final-only mode copy the other14 frozen models, explicitly marking
    # reuse; --all-cases actually refits all15 and is the consistency run.
    import shutil
    for f in folds:
        case=f['case_id'];folder=out/'models'/case;folder.mkdir(parents=True)
        if f not in active:
            shutil.copy2(ROOT/f'models/{case}/R0_PSO.joblib',folder/'R0_PSO.joblib');continue
        tr=[r for r in rows if r['family'] in f['fit_groups']];assert {r['curve_id'] for r in tr}==set(f['fit_curve_ids'])
        w=hierarchy_weights(tr,recipe['weight_levels']);x=np.asarray([r['x'] for r in tr],float);y=np.asarray([r['loss_pp'] for r in tr],float)
        model=ExtraTreesRegressor(**recipe['parameters'])
        start=time.perf_counter()
        with threadpool_limits(limits=1):model.fit(x,y,sample_weight=w)
        fit_seconds=time.perf_counter()-start
        start=time.perf_counter();joblib.dump(model,folder/'R0_PSO.joblib',compress=3);save_seconds=time.perf_counter()-start
        frozen=joblib.load(ROOT/f'models/{case}/R0_PSO.joblib');xx=np.asarray([s['x'] for c in load('data/evaluation_curves.json') for s in c['states']],float)
        delta=float(np.max(np.abs(frozen.predict(xx)-model.predict(xx))))
        comparison.append(dict(case_id=case,probe_states=len(xx),maximum_prediction_difference_pp=delta,training_rows=len(tr),train_curves=len(f['fit_curve_ids']),fit_families=len(f['fit_groups'])))
        timings.append(dict(case_id=case,training_rows=len(tr),tree_fit_seconds=fit_seconds,serialization_seconds=save_seconds,weight_sum=float(w.sum()),scope='model.fit plus threadpool-limit context entry/restore; PSO/features/model serialization excluded'))
        print('TRAINED',case,'rows',len(tr),'seconds',fit_seconds,'prediction_diff',delta,flush=True)
    write(out/'training_timings.json',timings);table(out/'training_timings.csv',timings);write(out/'prediction_consistency.json',comparison)
    for scheme in ['U0-E','Original_frozen']:
        dest=out/scheme;dest.mkdir();evaluate(dest,scheme,out/'models')
    write(out/'training_receipt.json',dict(refitted_cases=[f['case_id'] for f in active],reused_cases=[f['case_id'] for f in folds if f not in active],hyperparameter_searches=0,seed_searches=0,same_head_cal_test=True,refit_after_calibration=False,maximum_probe_prediction_difference_pp=max(r['maximum_prediction_difference_pp'] for r in comparison)))
