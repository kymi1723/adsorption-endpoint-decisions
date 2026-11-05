"""Release-local paths and exclusive output directories."""
from pathlib import Path
import csv, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
FINAL='original_fit_cal_to_transfer'
METHODS=('Learned','H1','H2','H3')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def load(name):return read(ROOT/name)
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def table(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or ['status']);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def output(path):
    p=Path(path).resolve()
    if p==ROOT or p.is_relative_to(ROOT/'models') or p.is_relative_to(ROOT/'data') or p.is_relative_to(ROOT/'reference'):raise ValueError('Output may not overwrite release inputs')
    p.mkdir(parents=True,exist_ok=False);return p
def identity(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
