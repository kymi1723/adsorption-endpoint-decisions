"""Paper table exports and calculated U0-E display tables, no model choices."""
import shutil
from .io import ROOT,load,table,write
def paper_tables(out):
    d=out/'paper_tables';d.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'reference/final_table_exports',d/'exact_supplied_text',dirs_exist_ok=True)
    rr=[r for r in load('reference/paper_tables/T01_policy_layer_metrics.json') if r['scheme']=='U0-E' and r['error_tolerance_pp']==5 and r['deleted_cal_family'] is None and r['batch_id'] in ['original79','transfer19'] and r['method'] in ['Learned','H1']]
    table(d/'Table2_U0_E_full_precision.csv',[{k:r[k] for k in ['batch_id','method','adopted_count','A','B','R','wait_min','n_observations']} for r in rr])
    wins=[r for r in load('reference/paper_tables/T07_layer_mean20_differences.json') if r['scheme']=='U0-E' and r['error_tolerance_pp']==5 and r['deleted_cal_family'] is None and r['batch_id'] in ['original79','transfer19'] and r['comparison']=='Learned-H1']
    table(d/'Table3_U0_E_full_precision.csv',wins)
    write(d/'table_sources.json',dict(Table2='reference/paper_tables/T01_policy_layer_metrics.json; filters U0-E,5pp,no calibration-family deletion; verified against fresh model/calibration output',Table3='reference/paper_tables/T07_layer_mean20_differences.json; same filters',exact_supplied_text='direct DOCX table-text exports, never claimed to be new calculations',laboratory_tables='data/laboratory/D34–D38; freshly inferred60min check in outputs/verification/laboratory'))
