"""Generate paper/SI plots from released original data, separately from references."""
import csv,shutil,os
import numpy as np
from .io import ROOT,load,write,table

def figures(out):
    os.environ.setdefault('MPLCONFIGDIR',str(out/'_mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from . import plot_support as support
    support.RUN=out
    for sub in ['figures/main','figures/supplement','tables','results']:(out/sub).mkdir(parents=True)
    from . import plot_original,plot_sensitivity,plot_archived_si,plot_calibration,plot_learning,plot_observation_budget,plot_agreement
    for mod in [plot_original,plot_sensitivity,plot_archived_si,plot_calibration,plot_learning,plot_observation_budget,plot_agreement]:mod.RUN=out
    # Each function consumes completed frozen summaries only. Main Tables2/3
    # use the separate U0-E evaluation entry, never these original-policy rows.
    plot_original.run();plot_sensitivity.run();plot_calibration.run();plot_archived_si.old_clock();plot_archived_si.cost_grid();plot_learning.run();plot_observation_budget.run();plot_agreement.run()
    # New final laboratory panels use the supplied D34–D38 data. They are not
    # the old single-curve Zheng plot. Numerical inference is checked elsewhere.
    with (ROOT/'data/laboratory/D34_laboratory_raw.csv').open(encoding='utf-8-sig') as f:raw=list(csv.DictReader(f))
    with (ROOT/'data/laboratory/D36_laboratory_prefixes.csv').open(encoding='utf-8-sig') as f:prefix=list(csv.DictReader(f))
    print('LAB_PLOT_COLUMNS',list(prefix[0]),flush=True)
    fig,axes=plt.subplots(1,3,figsize=(15,4.7));colors=['#17647e','#bd8032','#8176a3']
    times=sorted({float(r['t_min']) for r in raw});vals=np.array([[float(next(r['q_mg_g'] for r in raw if r['series']==cid and float(r['t_min'])==t)) for t in times] for cid in sorted({r['series'] for r in raw})])
    axes[0].errorbar(times,vals.mean(axis=0),yerr=vals.std(axis=0,ddof=1),fmt='o-',capsize=3,color=colors[0]);axes[0].axvline(60,ls=':',c='grey');axes[0].set(xlabel='Time (min)',ylabel='Uptake (mg/g)',title='a  Three parallel series; sample SD')
    truth=vals[:,times.index(120.)]
    # Values below are taken from the explicitly supplied prefix CSV, not a
    # newly chosen result. Verify command compares fresh inference to this CSV.
    def field(r,*names):
        for name in names:
            if name in r:return r[name]
        raise KeyError(names)
    at60=[r for r in prefix if float(field(r,'prefix_time_min','last_time_min','last_time','t_last_min','t_min','time_min'))==60]
    predicted=[float(field(r,'prediction_mg_g','PSO_q120_mg_g','q120_pred_mg_g','pred_q120_mg_g','q120_mg_g','PSO_q120')) for r in at60]
    xx=np.arange(3);axes[1].bar(xx-.17,predicted,.32,label='60-min forecast',color=colors[0]);axes[1].bar(xx+.17,truth,.32,label='Measured120min',color=colors[1]);axes[1].set(xticks=xx,xticklabels=['1','2','3'],xlabel='Series',ylabel='Uptake (mg/g)',title='b  Endpoint predictions and targets');axes[1].legend(fontsize=9)
    axes[2].bar([0,1],[60,120],color=[colors[0],colors[1]]);axes[2].set(xticks=[0,1],xticklabels=['Adopt at60\n5 observations','Target120\n7 observations'],ylabel='Time to estimate (min)',title='c  Decision resource use')
    fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(out/'figures/main'/('Fig6_laboratory.'+ext),dpi=220)
    plt.close(fig)
    rules=load('data/laboratory/D38_laboratory_config.json')['U0_E_thresholds'];fig,axes=plt.subplots(2,2,figsize=(10,7.5))
    for ax,method in zip(axes.flat,rules):
        for cid,color in zip(sorted({r['series'] for r in prefix}),colors):
            rr=[r for r in prefix if r['series']==cid];xx=[float(field(r,'prefix_time_min','last_time_min','last_time','t_last_min','t_min','time_min')) for r in rr]
            key={'Learned':('learned_score_pp','Learned_score_pp','Learned','q_pp'), 'H1':('H1_score_pp','H1_pp','H1'),'H2':('H2_score_pp','H2_pp','H2'),'H3':('H3_score_pp','H3_pp','H3')}[method]
            yy=[float(field(r,*key)) if field(r,*key) not in ['', 'NA','None','null'] else np.nan for r in rr];ax.plot(xx,yy,'o-',color=color,label=cid)
        ax.axhline(rules[method],c='#b33b32',ls='--');ax.axvline(60,c='grey',ls=':');ax.set(title=method,xlabel='Last observed time (min)',ylabel='Score (pp)');ax.grid(alpha=.15)
    axes.flat[0].legend(fontsize=8);fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(out/'figures/supplement'/('FigS11_laboratory_scores.'+ext),dpi=220)
    plt.close(fig)
    # Retain all plotting input tables with clear original/robustness namespaces.
    shutil.copytree(ROOT/'reference/paper_tables',out/'plot_data/paper_tables');shutil.copytree(ROOT/'reference/plot_inputs',out/'plot_data/additional_inputs');shutil.copytree(ROOT/'data/laboratory',out/'plot_data/laboratory')
    organize(out)
    from .tables import paper_tables
    paper_tables(out)
    write(out/'figure_generation_receipt.json',dict(canonical_paper_panels=18,original_plot_bodies_reused=True,final_word_layout_byte_identity_claim=False,exact_supplied_media='reference/final_manuscript_media',models_refitted=0,numerical_input_sources='all in plot_data; U0-E tables have their own evaluation output'))

def organize(out):
    mapping={
      'Figure1':'figures/main/Fig1_roles_and_stopping',
      'Figure2':'figures/main/Fig2_selected_policy_comparison',
      'Figure3':'figures/main/Fig3_all_family_cost_differences',
      'Figure4':'figures/main/Fig4_all20_plateau_tradeoff',
      'Figure5':'figures/main/Fig5_fixed_case_trajectories',
      'Figure6':'figures/main/Fig6_laboratory',
      'FigureS1':'figures/main/B03_calibration_only_diagnostics',
      'FigureS2':'figures/supplement/SF01_old_clock_boundary',
      'FigureS3':'figures/main/F04_all20_cost_differences',
      'FigureS4':'figures/R01_uniform_calibration',
      'FigureS5':'figures/R02_tolerance_distinction',
      'FigureS6':'figures/R03_paired_family_uncertainty',
      'FigureS7':'figures/R04_calibration_family_deletion',
      'FigureS8a':'results/score_learning_curve',
      'FigureS8b':'results/policy_learning_curve',
      'FigureS9':'figures/paired_changes',
      'FigureS10':'figures/Fan_Du_real_points_and_fixed_forecasts',
      'FigureS11':'figures/supplement/FigS11_laboratory_scores'}
    dest=out/'paper_numbered';dest.mkdir(exist_ok=True);rows=[]
    for label,path in mapping.items():
        for ext in ['png','svg']:
            src=(out/path).with_suffix('.'+ext)
            if src.exists():shutil.copy2(src,dest/(label+'.'+ext))
        assert (dest/(label+'.png')).exists(),label
        rows.append(dict(paper_id=label,generated_source=path,numbered_png='paper_numbered/'+label+'.png',exact_word_layout=False))
    table(out/'figure_number_map.csv',rows);write(out/'figure_number_map.json',rows)
