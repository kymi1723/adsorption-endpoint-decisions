from .plot_support import *
import matplotlib.pyplot as plt
def run():
    pairs=read(RUN/'data/sampling_paired_scores.json')
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    for ax,baseline,label in zip(axes,['first3','fullgrid_wait60'],['First5 minus first3','First5 minus +1 within60min']):
        rr=sorted([r for r in pairs if r['model']=='nested_failure_constrained' and r['chosen_profile']=='fixed5' and r['baseline_profile']==baseline],key=lambda r:r['delta_RMSE_pp'])
        ax.scatter(range(86),[r['delta_RMSE_pp'] for r in rr],s=17,c=['#cc3311' if r['new_failure'] else '#009988' if r['rescued_failure'] else '#555555' for r in rr])
        ax.axhline(0,color='black',lw=.8);ax.set(xlabel='All 86 curves, sorted by paired difference',ylabel='RMSE difference (pp); positive = worse',title=label);ax.grid(alpha=.15)
    fig.suptitle('Nested correction: a lower mean can accompany more failures')
    fig.text(.01,.008,'Red: newly crosses 5 pp; green: rescues a baseline failure; gray: same failure status. Full paired scores and family changes are retained in CSV.',fontsize=8)
    fig.get_layout_engine().set(rect=(0,.065,1,.91));fig.savefig(RUN/'figures/paired_changes.png',dpi=170);plt.close(fig)
