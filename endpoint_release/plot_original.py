"""Journal-facing layouts from accepted table cells; no inference or policy replay."""
from .plot_support import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
COLORS={'R2':'#17647e','H1':'#bd8032','H2':'#8176a3','H3':'#5b9275','F_PSO':'#8393a6','F_Last':'#c25b55','R0':'#b6bdc2'}
NAMES={'R2':'Learned','H1':'Plateau','H2':'Forecast stability','H3':'Latest-point error','F_PSO':'Fixed PSO','F_Last':'Fixed last','R0':'Measure target'}
ORDER=['original79','transfer19','historical_external15','N4_confirmation01','C01_confirmation02','remaining_queue03']
LABELS=['Held family\n79 / 14','Transfer\n19 / 6','Historical\n15 / 6','Aerogel\n1 / 1','LDH clay\n6 / 1','New queue\n10 / 3']
def run():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
    manifest=[]
    def save(fig,name,title,sources,folder='main'):
        for ext in ['png','svg']:fig.savefig(RUN/'figures'/folder/(name+'.'+ext),dpi=300)
        plt.close(fig);manifest.append(dict(id=name,title=title,folder=folder,png=rel(RUN/'figures'/folder/(name+'.png')),svg=rel(RUN/'figures'/folder/(name+'.svg')),sources=[rel(p) for p in sources],scientific_recalculation=False))
    fig,axes=plt.subplots(1,2,figsize=(13,6),gridspec_kw={'width_ratios':[1,1.35]});a,b=axes;a.axis('off');b.axis('off')
    a.text(0,1,'a  Evaluation roles',fontsize=14,weight='bold',transform=a.transAxes)
    texts=['Held-family development: 79 curves / 14 families\n14 different fit/cal/test configurations','Transfer development: 19 / 6\nFinal fit 53 / 7; calibration 26 / 7','Historical external: 15 / 6\nPreviously evaluated; now contacted','Aerogel 1 / 1; LDH clay 6 / 1\nLDH: prior qualitative-response contact','Later three-source queue: 10 / 3\nAll new simple-rule comparisons retrospective']
    for i,t in enumerate(texts):a.text(.02,.85-i*.185,t,transform=a.transAxes,fontsize=13.5,va='top')
    b.set(xlim=(0,10),ylim=(0,7));b.text(0,6.8,'b  Prediction adoption or continued measurement',fontsize=13,weight='bold')
    boxes=[(2,5.3,6,1,'Real complete prefix, k >= 3\nKnown target clock; initial-inventory scale'),(2,3.65,6,1,'PSO endpoint forecast\nAvailable score <= calibrated threshold?'),(.05,1.65,4.1,1,'Yes: adopt current forecast\nFirst passing prefix'),(5.5,1.65,4.1,1,'No: acquire next real point\nOr measure target as fallback')]
    for x,y,w,h,t in boxes:b.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',fc='#edf3f6',ec='#355564',clip_on=False));b.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=13.5)
    for p,q in [((5,5.2),(5,4.8)),((4,3.5),(2.1,2.8)),((6,3.5),(7.6,2.8))]:b.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=14,color='#355564'))
    b.text(5,.7,'No generated observation; no post-target input\n5 pp tolerance and 5% empirical goal are distinct',ha='center',fontsize=13.5);fig.tight_layout();save(fig,'Fig1_roles_and_stopping','Evaluation roles and stopping',[BENCH/'protocol/original_folds.json',EVID/'tables/T05_confirmation_and_development_layers.json'])
    rows=read(BENCH/'tables/T01_all_method_comparison.json');fig,axes=plt.subplots(4,2,figsize=(14,12),sharex='col',gridspec_kw={'width_ratios':[1,1.8]})
    for col,cohorts in enumerate([ORDER[:2],ORDER[2:]]):
        for j,m in enumerate(COLORS):
            rr=[next(r for r in rows if r['batch_id']==c and r['method']==m) for c in cohorts];xx=np.arange(len(cohorts))+(j-3)*.105
            for ri,(key,scale) in enumerate([('A',100),('R',100),('wait_min',1),('n_observations',1)]):
                ax=axes[ri,col];ax.bar(xx,[r[key]*scale if r[key] is not None else np.nan for r in rr],.10,color=COLORS[m],label=NAMES[m]);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        for ri in range(4):axes[ri,col].set_xticks(np.arange(len(cohorts)),[LABELS[ORDER.index(c)] for c in cohorts],fontsize=14)
        for j,m in enumerate(COLORS):
            for k,c in enumerate(cohorts):
                r=next(r for r in rows if r['batch_id']==c and r['method']==m);x=k+(j-3)*.105
                if r['R'] is None:axes[1,col].text(x,2,'NA',ha='center',va='bottom',rotation=90,fontsize=14,color=COLORS[m])
                elif r['R']==0:
                    axes[1,col].plot(x,0,'o',color=COLORS[m],ms=5,clip_on=False);axes[1,col].text(x,2,'0',ha='center',va='bottom',fontsize=14,color=COLORS[m])
        axes[1,col].set_ylim(-4,30 if col==0 else 105)
        axes[1,col].axhline(5,c='#a94339',ls=':',lw=1)
    for i,t in enumerate(['Adoption A (%)','Out-of-tolerance R (%)','Waiting (min)','Observations']):axes[i,0].set_ylabel(t)
    axes[0,0].set_title('Development layers');axes[0,1].set_title('Later layers with distinct contact histories');axes[0,0].set_ylim(0,110);axes[0,1].set_ylim(0,110)
    for i,ax in enumerate(axes.flat):ax.text(.015,.93,chr(97+i),transform=ax.transAxes,fontsize=15,weight='bold');ax.tick_params(labelsize=14)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,ncol=4,loc='upper center',bbox_to_anchor=(.5,1.02),fontsize=14);fig.tight_layout(rect=(0,0,1,.97));save(fig,'Fig2_selected_policy_comparison','Selected-policy comparison',[BENCH/'tables/T01_all_method_comparison.json'])
    rr=read(BENCH/'tables/ST03_R2_minus_H_family_mean20.json');lookup=read(EVID/'tables/ST03_source_family_index.json');families=[]
    for batch in ORDER:
        for r in rr:
            if r['batch_id']==batch and r['canonical_group_id'] not in [x[1] for x in families]:families.append((batch,r['canonical_group_id']))
    vals=np.array([[next(r['mean20_delta_J_pp'] for r in rr if r['batch_id']==batch and r['canonical_group_id']==g and r['comparison']=='R2-'+m) for m in ['H1','H2','H3']] for batch,g in families]);vals[np.abs(vals)<1e-10]=0;limit=max(abs(vals.min()),abs(vals.max()));fig,ax=plt.subplots(figsize=(10,12));im=ax.imshow(vals,cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='auto')
    labels=[]
    for batch,g in families:
        z=next(x for x in lookup if x['family_id']==g);labels.append(z['family_label']+' | '+' / '.join(z['source_ids']))
    ax.set_yticks(range(len(labels)),labels,fontsize=11);ax.set_xticks(range(3),['a  Learned - H1','b  Learned - H2','c  Learned - H3'],fontsize=12);ax.tick_params(axis='x',top=True,labeltop=True,bottom=False,labelbottom=False)
    for i in range(len(vals)):
        for j in range(3):ax.text(j,i,f'{vals[i,j]:.2f}',ha='center',va='center',fontsize=11,color='white' if abs(vals[i,j])>.65*limit else '#1f3240')
    running=0
    for batch in ORDER:
        running+=sum(b==batch for b,g in families)
        if running<len(families):ax.axhline(running-.5,c='black',lw=1)
    fig.colorbar(im,ax=ax,label='Family mean20 loss difference (pp-equivalent)',shrink=.65);fig.tight_layout();save(fig,'Fig3_all_family_cost_differences','Every-family costs',[BENCH/'tables/ST03_R2_minus_H_family_mean20.json',EVID/'tables/ST03_source_family_index.json'])
    cost=read(BENCH/'tables/T03_R2_minus_H_cost20.json');limit=max(abs(r['delta_J_pp']) for r in cost if r['comparison']=='R2-H1');fig,axes=plt.subplots(3,2,figsize=(11,12),layout='constrained')
    for panel,(ax,batch,title) in enumerate(zip(axes.flat,ORDER,LABELS)):
        rs=[r for r in cost if r['batch_id']==batch and r['comparison']=='R2-H1'];v=np.array([[next(r['delta_J_pp'] for r in rs if r['lambda_pp']==l and r['mu_pp_per_min']==mu) for mu in [0,.025,.05,.1]] for l in [0,.5,1,2,5]]);im=ax.imshow(v,cmap='RdBu_r',vmin=-limit,vmax=limit,aspect='auto');ax.set_xticks(range(4),['0','.025','.05','.1']);ax.set_yticks(range(5),['0','.5','1','2','5']);ax.set(xlabel='Waiting weight μ (pp/min)',ylabel='Measurement weight λ (pp)',title=chr(97+panel)+'  '+title.replace('\n',' | '))
        for i in range(5):
            for j in range(4):ax.text(j,i,f'{v[i,j]:.2f}',ha='center',va='center',fontsize=11.5,color='white' if abs(v[i,j])>.6*limit else '#243947')
    fig.colorbar(im,ax=list(axes.flat),label='Learned - plateau loss (pp-equivalent)',shrink=.7);save(fig,'Fig4_all20_plateau_tradeoff','Full cost grid against plateau',[BENCH/'tables/T03_R2_minus_H_cost20.json'])
    cases=read(EVID/'tables/F05_representative_case_data.json');hrows=read(BENCH/'results/H_curve_results.json')
    fig=plt.figure(figsize=(12.4,10.6));gs=fig.add_gridspec(4,3,height_ratios=[3,1.1,3,1.1],hspace=.65,wspace=.48)
    titles=['CMC-MMT / CR / 25 C','Chitosan-BT / AB10B / 100','Chitosan-BT / AB10B / 200','CHS-BZ/MT/AL / RB19 / C20','Fan / tolerance violation','Aerogel / H3 failure'];case_records=[]
    from matplotlib.lines import Line2D
    for i,(c,title) in enumerate(zip(cases,titles)):
        ax=fig.add_subplot(gs[(i//3)*2,i%3]);tabax=fig.add_subplot(gs[(i//3)*2+1,i%3]);tabax.axis('off');obs=c['observations'];pred=c['saved_forecasts'];t=c['target'];learned=c['frozen_R2_action']
        policies=[('Learned',learned,'*','#17647e'),('H1',next(r for r in hrows if r['curve_id']==c['curve_id'] and r['method']=='H1'),'^','#bd8032'),('H3',next(r for r in hrows if r['curve_id']==c['curve_id'] and r['method']=='H3'),'s','#5b9275')]
        ax.plot([p['time_min'] for p in obs],[100*p['fraction'] for p in obs],'o-',c='#263e4b',lw=1,ms=3)
        ax.plot([p['time_min'] for p in pred],[100*p['prediction'] if p['prediction'] is not None else np.nan for p in pred],'--',c='#79a8b9',lw=1)
        ax.axhspan(100*t['fraction_lower'],100*t['fraction_upper'],color='#d7b879',alpha=.22);ax.axhline(100*t['fraction'],c='#8e773d',ls=':',lw=.7)
        cells=[]
        for name,a,marker,color in policies:
            if a['adopted']:ax.scatter([a['adoption_time_min']],[100*a['prediction']],marker=marker,s=115 if name=='Learned' else 65,facecolor=color,edgecolor='#b3302b' if a['wrong_adoption'] else color,linewidths=2 if a['wrong_adoption'] else 1,zorder=8)
            cells.append([name,f"{a['adoption_time_min']:.1f}"+('†' if not a['adopted'] else ''),f"{a['absolute_error_pp']:.2f}"])
            case_records.append(dict(panel=chr(97+i),curve_id=c['curve_id'],policy=name,state_id=a['state_id'],adopted=a['adopted'],time_min=a['adoption_time_min'],error_pp=a['absolute_error_pp'],out_of_tolerance=a['wrong_adoption'],source_file=rel(EVID/'tables/F05_representative_case_data.json') if name=='Learned' else rel(BENCH/'results/H_curve_results.json')))
        table=tabax.table(cellText=cells,colLabels=['Policy','t / min','e / pp'],cellLoc='center',loc='center');table.auto_set_font_size(False);table.set_fontsize(12.5);table.scale(1,1.3)
        for cell in table.get_celld().values():cell.set_edgecolor('#d9d9d9')
        ax.set(title=chr(97+i)+'  '+title,xlabel='Last observation time (min)',ylabel='Removed fraction (%)');ax.tick_params(labelsize=12.5);ax.title.set_fontsize(13);ax.xaxis.label.set_size(12.5);ax.yaxis.label.set_size(12.5);ax.grid(alpha=.15)
    handles=[Line2D([0],[0],color='#263e4b',marker='o',lw=1,label='Real observations'),Line2D([0],[0],color='#79a8b9',ls='--',label='Endpoint forecasts (offline replay)')]+[Line2D([0],[0],color=color,marker=marker,ls='',ms=9,label=name) for name,marker,color in [('Learned','*','#17647e'),('H1','^','#bd8032'),('H3','s','#5b9275')]]
    fig.legend(handles=handles,ncol=3,loc='lower center',fontsize=12.5);fig.text(.5,.065,'† Target measured; replay error is zero by definition. Red outlines: error > 5 pp.',ha='center',fontsize=12.5);fig.subplots_adjust(bottom=.13,top=.96)
    save(fig,'Fig5_fixed_case_trajectories','Learned and simple-rule actions in six fixed cases',[EVID/'tables/F05_representative_case_data.json',BENCH/'results/H_curve_results.json']);save_table('Fig5_action_markers',case_records)
    for name,source,title in [('FigS1_calibration_only',BENCH/'figures/main/B03_calibration_only_diagnostics','Calibration-only diagnostics'),('FigS2_old_clock_boundary',BENCH/'figures/supplement/SF01_old_clock_boundary','Earlier clock sensitivity'),('FigS3_cal_selected_simple',BENCH/'figures/main/F04_all20_cost_differences','Original cal-selected simple comparator')]:
        for ext in ['.png','.svg']:shutil.copy2(source.with_suffix(ext),RUN/'figures/supplement'/(name+ext))
        manifest.append(dict(id=name,title=title,folder='supplement',png=rel(RUN/'figures/supplement'/(name+'.png')),svg=rel(RUN/'figures/supplement'/(name+'.svg')),sources=[rel(source.with_suffix('.png'))],unchanged_copy=True))
    write(RUN/'figures/figure_manifest.json',manifest);log('Five manuscript figures laid out; B01 crowding removed by shorter split labels; three SI figures copied',new_metric_calculations=0)
if __name__=='__main__':run()
