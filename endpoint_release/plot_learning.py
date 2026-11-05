from .plot_support import *
import matplotlib.pyplot as plt
def run():
    scores=read(RUN/'results/score_distribution_by_m.json');pol=read(RUN/'results/policy_distribution_by_m.json')
    def draw(ax,dist,metric,title,unit):
        rr=[r for r in dist if r['metric']==metric];x=[r['m'] for r in rr];y=[r['mean'] for r in rr]
        ax.plot(x,y,'o-',c='#087e8b',label='subset-equal mean');many=[r for r in rr if r['subsets']>1]
        ax.fill_between([r['m'] for r in many],[r['minimum'] for r in many],[r['maximum'] for r in many],color='#087e8b',alpha=.18,label='all-combination range (not CI)')
        ax.scatter([7],[rr[-1]['mean']],marker='*',s=160,c='#b65a09',zorder=4,label='m=7: original R2 reused')
        ax.set_title(title);ax.set_xlabel('Number of training sources (m)');ax.set_ylabel(unit);ax.set_xticks(range(1,8));ax.grid(alpha=.2)
    fig,axs=plt.subplots(1,2,figsize=(12,4.7))
    for ax,k,title in zip(axs,['score_MAE_pp','score_RMSE_pp'],['Test risk-score MAE','Test risk-score RMSE']):draw(ax,[r for r in scores if r['role']=='test'],k,title,'Score error (pp)')
    h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,fontsize=9);fig.suptitle('Fixed6-source /19-curve transfer test; combinations share the same calibration and test');fig.tight_layout(rect=(0,.09,1,.94));fig.savefig(RUN/'results/score_learning_curve.png',dpi=160);plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    for ax,k,title,unit in zip(axs.flat,['A','R','wait_min','new_measurements'],['Calibrated test adoption A','Conditional above5 rate R (null excluded)','Waiting after t3','Measurements added after first3'],['Proportion','Conditional proportion','Minutes','Measurements']):draw(ax,pol,k,title,unit)
    h,l=axs.flat[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,fontsize=9);fig.suptitle('Original calibration algorithm per head; min/max show composition sensitivity, not confidence');fig.tight_layout(rect=(0,.07,1,.95));fig.savefig(RUN/'results/policy_learning_curve.png',dpi=160);plt.close(fig)
