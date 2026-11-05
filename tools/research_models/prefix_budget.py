"""Reusable inventory-bounded PSO prefix fit, matching the existing baseline."""
import numpy as np
from scipy.optimize import least_squares


def response(time_min,fe,tau_min):
    t=np.asarray(time_min,dtype=float)
    return fe*t/(tau_min+t)


def fit_prefix(time_min,fraction):
    t,y=np.asarray(time_min,dtype=float),np.asarray(fraction,dtype=float)
    fits=[]
    for fe in [min(.9999,max(.001,float(y.max()))),.9999]:
        for tau in [max(1e-5,float(t[0])*.1),float(np.median(t)),float(t[-1])*2]:
            f=least_squares(lambda z:response(t,z[0],np.exp(z[1]))-y,[fe,np.log(tau)],
                bounds=([0.,np.log(1e-6)],[1.,np.log(1e6)]),ftol=1e-11,xtol=1e-11,gtol=1e-11,max_nfev=3000)
            if f.success:fits.append(f)
    if not fits:raise RuntimeError("No successful prefix optimizer")
    f=min(fits,key=lambda a:float(a.fun@a.fun))
    return dict(fe=float(f.x[0]),tau_min=float(np.exp(f.x[1])),training_SSE=float(f.fun@f.fun),
                fe_inventory_bound_active=bool(f.x[0]>.9999),optimizer_success=True)


def cached_prefix_matches(record,points):
    parameters=record.get("parameters",record)
    if not all(k in parameters for k in ("fe","tau_min","training_SSE")):return False
    if not 0<=parameters["fe"]<=1 or not 1e-6<=parameters["tau_min"]<=1e6:return False
    if record.get("input_point_ids") and record["input_point_ids"]!=[p["point_id"] for p in points]:return False
    if record.get("training_times_min") and not np.allclose(record["training_times_min"],[p["time_min"] for p in points],rtol=0,atol=1e-8):return False
    pred=response([p["time_min"] for p in points],parameters["fe"],parameters["tau_min"])
    sse=float(np.sum((pred-np.array([p["removal_fraction"] for p in points]))**2))
    return abs(sse-parameters["training_SSE"])<=1e-10
