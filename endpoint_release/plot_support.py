"""IO adapter for extracted plotting bodies; only explicit released tables."""
from pathlib import Path
import json,shutil
from .io import ROOT,read as read_json,write,table
RUN=ROOT/'outputs/figures'
BENCH=ROOT/'reference/benchmark';EVID=ROOT/'reference/evidence';PREV=BENCH
C01=ROOT/'reference/C01';N4=ROOT/'reference/N4';FINAL='original_fit_cal_to_transfer'
ORDER=['original79','transfer19','historical_external15','N4_confirmation01','C01_confirmation02','remaining_queue03']
LABELS=['Original79','Transfer19','Historical15','Aerogel1','LDH–clay6','Queue10']
def read(path):
    p=Path(path)
    if p.exists():return read_json(p)
    name=p.name
    for d in [ROOT/'reference/plot_inputs',ROOT/'reference/paper_tables',ROOT/'reference/paper_tables/original']:
        q=d/name
        if q.exists():return read_json(q)
    if name=='frozen_H_rules.json':return read_json(ROOT/'reference/original_H_rules.json')
    raise FileNotFoundError('Explicit released plot input missing: '+str(path))
def rel(path):
    p=Path(path)
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.name
def save_table(name,rows,folder='tables'):
    table(RUN/folder/(name+'.csv'),rows);write(RUN/folder/(name+'.json'),rows)
def log(event,**kwargs):print('PLOT',event,kwargs,flush=True)
def save(fig,name,title,caption,sources,folder='main',data=None):
    import matplotlib.pyplot as plt
    d=RUN/'figures'/folder;d.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg']:fig.savefig(d/(name+'.'+ext),dpi=220)
    plt.close(fig)
