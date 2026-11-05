from .plot_support import *
import matplotlib.pyplot as plt
def run():
    out=RUN/'figures';colors=['#176b9e','#e59833','#4a9d78']
    cases=read(RUN/'results/case_evidence_layers.json');fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,cid in zip(axes,['Fan2022_CMP30_CR_C950_T303_Fig6a','Du2024_1p0GAMt_AcidOrange7_C50']):
        c=next(c for c in cases if c['curve_id']==cid);s=c['posthoc_future']['real_pool_and_target_geometry'];target=c['posthoc_future']['target'];p=c['current_prefix_visible'];allp=s['pool'];ax.plot([v['time_min'] for v in allp]+[target['time_min']],[v['fraction']*100 for v in allp]+[target['fraction']*100],'.-',color='#a8a8a8',label='Real readings (future: posthoc)');k=p['k'];ax.scatter(p['input_times_min'],[v['fraction']*100 for v in allp[:k]],color='#173f62',zorder=3,label='Inputs at fixed position')
        for model,color in zip(['PSO','Last','PFO'],colors):ax.scatter([target['time_min']],[p[model+'_prediction']*100],marker='x',color=color,s=55,label=model+' forecast')
        ax.axvline(p['last_observation_min'],color='#777',ls=':',lw=1);ax.set(xlabel='Real sampling time (min)',ylabel='Removed fraction ×100 (%)',title=('Fan: historical R2 adopted k4' if cid.startswith('Fan') else 'Du1.0: CSTOP k4; R2 fallback'));ax.legend(fontsize=7)
    fig.suptitle('Forecasts use current prefix only; grey future readings explain errors retrospectively');fig.tight_layout();fig.savefig(out/'Fan_Du_real_points_and_fixed_forecasts.png',dpi=180);plt.close(fig)
