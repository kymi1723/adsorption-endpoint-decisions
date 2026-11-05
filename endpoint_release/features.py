"""Original function bodies extracted without numerical changes; see provenance/source_manifest.json."""
import numpy as np
from tools.research_models.prefix_budget import response

def state_vector(s,m,parent):
    t=np.array([r['time_min'] for r in s['inputs']]);y=np.array([r['fraction'] for r in s['inputs']]);last=t[-1]
    q=np.array([r['time_min'] for r in s['queries']]);slog=lambda v:float(np.sign(v)*np.log1p(abs(v)))
    x=[len(t),float(np.log1p(t[0])),float(np.log1p(last)),float(np.log(q.min()/last)),float(np.log(q.max()/last)),float(y[-1]),float(np.ptp(y)),
        slog((y[-1]-y[-2])/(t[-1]-t[-2])*last),slog((y[-1]-y[0])/(last-t[0])*last)]
    if m['available']:
        p=m['parameters'];v=response(q,p['fe'],p['tau_min'])
        x += [float(np.log1p(np.sqrt(p['training_SSE']/len(t))*100)),p['fe'],float(np.log1p(p['tau_min']/last)),float(v.mean()),float(np.ptp(v)),
            float(np.log1p(np.sqrt(np.mean((v-y[-1])**2))*100)),int(m['fe_bound']),int(m['tau_bound']),0]
    else:x += [0.,0.,0.,float(y[-1]),0.,0.,0,0,1]
    if len(t)>3 and parent is not None and parent['available']:
        p=parent['parameters'];error=abs(float(response([last],p['fe'],p['tau_min'])[0])-y[-1])*100
        x += [float(np.log1p(error)),1]
    else:x += [0.,0]
    assert len(x)==20 and np.isfinite(x).all()
    return x
