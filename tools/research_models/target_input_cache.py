"""Query-independent PSO input identity and bounded worker for task migrations."""
import hashlib,json,time
from tools.research_models.prefix_budget import fit_prefix

def input_identity(curve_id,inputs,optimizer,code_sha256):
    obj=dict(curve_id=curve_id,inputs=[dict(point_id=p['point_id'],time_min=float(p['time_min']),fraction=float(p['fraction'])) for p in inputs],optimizer=optimizer,fit_code_sha256=code_sha256)
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def fit_job(job):
    from threadpoolctl import threadpool_limits
    sid,key,inputs=job;start=time.monotonic()
    try:
        with threadpool_limits(limits=1):par=dict(available=True,**fit_prefix([p['time_min'] for p in inputs],[p['fraction'] for p in inputs]))
    except (RuntimeError,ValueError,FloatingPointError) as e:par=dict(available=False,reason=type(e).__name__+': '+str(e))
    return dict(state_id=sid,fit_key=key,parameters=par,available=par['available'],category='new_fit',seconds=time.monotonic()-start,source='this_task_missing_input_subset',source_record=sid)
