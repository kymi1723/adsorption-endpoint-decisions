from .plot_support import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def run():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'svg.fonttype':'none','savefig.bbox':'tight','axes.spines.top':False,'axes.spines.right':False})
    rows=read(RUN/'tables/T01_policy_layer_metrics.json');manifest=[]
    def get(batch,method,scheme,tol=5,drop=None):return next(r for r in rows if r['batch_id']==batch and r['method']==method and r['scheme']==scheme and r['error_tolerance_pp']==tol and r['deleted_cal_family']==drop)
    def save(fig,name,caption,sources):
        for ext in ['png','svg']:fig.savefig(RUN/'figures'/(name+'.'+ext),dpi=260)
        plt.close(fig);manifest.append(dict(id=name,png=rel(RUN/'figures'/(name+'.png')),svg=rel(RUN/'figures'/(name+'.svg')),caption=caption,sources=[rel(RUN/p) for p in sources]))
    schemes=['Original_frozen','U0-E','U25-E','U0-Q','U25-Q'];labels=['Original','U0-E','U25-E','U0-Q','U25-Q'];fig,axes=plt.subplots(2,2,figsize=(12,8.5));colors=['#246e8b','#b77a35']
    for j,b in enumerate(['original79','transfer19']):
        for ax,key,factor,label in [(axes[0,0],'A',100,'Delta adoption A (percentage points)'),(axes[0,1],'R',100,'Delta conditional R (percentage points)'),(axes[1,0],'n_observations',1,'Delta observations'),(axes[1,1],'wait_min',1,'Delta waiting (min)')]:
            values=[factor*(get(b,'Learned',s)[key]-get(b,'H1',s)[key]) for s in schemes];ax.plot(np.arange(5),values,'o-',color=colors[j],label='Original79' if j==0 else 'Transfer19');ax.set_xticks(np.arange(5),labels);ax.set_ylabel(label);ax.axhline(0,c='#777',lw=.7);ax.grid(alpha=.15)
    axes[0,0].legend();fig.suptitle('Learned minus plateau: all four predefined calibration schemes');fig.tight_layout();save(fig,'R01_uniform_calibration','Four common calibration algorithms, no test-based choice. Counts and minutes precede scenario loss. Negative resource differences favour Learned; rates are source equal.',['tables/T01_policy_layer_metrics.json'])
    fig,axes=plt.subplots(2,2,figsize=(11,8),sharex=True)
    for i,b in enumerate(['original79','transfer19']):
        for m,color in [('Learned','#246e8b'),('H1','#b77a35')]:
            for scheme,ls,label in [('Original_frozen','--','Fixed actions; reclassify error'),('U0-E','-','Recalibrate at each tolerance')]:
                rr=[get(b,m,scheme,t) for t in [3,5,7]]
                for ax,key in [(axes[i,0],'A'),(axes[i,1],'R')]:ax.plot([3,5,7],[100*r[key] if r[key] is not None else np.nan for r in rr],marker='o',ls=ls,c=color,label=m+' / '+label);ax.grid(alpha=.15)
        axes[i,0].set_ylabel(('Original79' if i==0 else 'Transfer19')+' adoption A (%)');axes[i,1].set_ylabel('Conditional out-of-tolerance R (%)');axes[i,1].axhline(5,c='#a84338',ls=':',lw=1)
    for ax in axes[1]:ax.set_xlabel('Single-prediction error tolerance (pp)');ax.set_xticks([3,5,7])
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,fontsize=9);fig.tight_layout(rect=(0,.12,1,1));save(fig,'R02_tolerance_distinction','Dashed curves retain original actions/resources; solid curves recalibrate U0-E thresholds using only calibration targets. Five-pp centre is reused, not recomputed.',['tables/T01_policy_layer_metrics.json'])
    boot=read(RUN/'tables/T09_cluster_bootstrap_intervals.json');fig,axes=plt.subplots(1,3,figsize=(14,5.8),sharey=True);bs=['original79','transfer19','historical_external15','remaining_queue03'];names=['Original79 / 14 families','Transfer19 / 6','Historical15 / 6','Queue03 / 3']
    for ax,key,factor,title in zip(axes,['delta_A','delta_n_observations','delta_wait_min'],[100,1,1],['Delta adoption A (percentage points)','Delta observations','Delta waiting (min)']):
        for j,scheme in enumerate(['Original_frozen','U0-E']):
            rr=[next(r for r in boot if r['batch_id']==b and r['scheme']==scheme and r['method']=='Learned-H1' and r['metric']==key) for b in bs];y=np.arange(4)+(j-.5)*.16
            for yy,r in zip(y,rr):ax.plot([factor*r['lower'],factor*r['upper']],[yy,yy],c=colors[j],lw=2);ax.plot(factor*r['median'],yy,'o',c=colors[j])
        ax.axvline(0,c='#555',lw=.8);ax.set_xlabel(title);ax.grid(axis='x',alpha=.15)
    axes[0].set_yticks(np.arange(4),names);axes[0].invert_yaxis();fig.suptitle('Conditional paired family resampling: 2.5–97.5 percentiles, 2000 draws',fontsize=14);fig.text(.5,.01,'Blue: original actions; orange: U0-E. One-family batches have no source-variation intervals. Not population guarantees.',ha='center',fontsize=10);fig.tight_layout(rect=(0,.06,1,.94));save(fig,'R03_paired_family_uncertainty','Same family draws across methods and Original/U0-E; duplicate family instances retained. These are descriptive conditional distributions, not training uncertainty or distribution-free confidence bounds.',['tables/T09_cluster_bootstrap_intervals.json'])
    rules=read(RUN/'protocol/selected_rules.json');drops=[r['deleted_cal_family'] for r in rules if r['method']=='Learned' and r['deleted_cal_family']];idx=read(EVID/'tables/ST03_source_family_index.json');labels=[next(r['family_label'] for r in idx if r['family_id']==g) for g in drops];fig,axes=plt.subplots(2,2,figsize=(12,8))
    for j,m in enumerate(['Learned','H1']):
        base=next(r for r in rules if r['case_id']==FINAL and r['method']==m and r['scheme']=='U0-E' and r['error_tolerance_pp']==5);values=[next(r['threshold_pp'] for r in rules if r['method']==m and r['deleted_cal_family']==g) for g in drops];axes[0,j].plot(range(7),values,'o-',c=colors[j]);axes[0,j].axhline(base['threshold_pp'],c='#777',ls='--');axes[0,j].set_title(m+' calibrated threshold');axes[0,j].set_ylabel('Method-specific score threshold (pp)')
        for b,color,label in [('remaining_queue03',colors[j],'Queue03 test R'),('transfer19','#7c78a1','Transfer19 test R')]:axes[1,j].plot(range(7),[100*get(b,m,'U0-E',5,g)['R'] if get(b,m,'U0-E',5,g)['R'] is not None else np.nan for g in drops],'o-',c=color,label=label)
        axes[1,j].axhline(5,c='#a84338',ls=':');axes[1,j].set_ylabel('Conditional out-of-tolerance R (%)');axes[1,j].legend(fontsize=9)
    for ax in axes.flat:ax.set_xticks(range(7),labels);ax.set_xlabel('Omitted calibration family (G labels in source index)');ax.grid(alpha=.15)
    fig.tight_layout();save(fig,'R04_calibration_family_deletion','Seven one-family calibration deletions at fixed final model/U0-E/5pp. Threshold axes are method-specific. Test responses only score selected rules; versions are not selected by test results.',['protocol/selected_rules.json','tables/T14_cal_family_deletion_changes.json'])
    write(RUN/'figures/figure_manifest.json',manifest);log('Four sensitivity figures generated from completed tables',figures=4)
if __name__=='__main__':run()
