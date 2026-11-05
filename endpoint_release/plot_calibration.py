from .plot_support import *
import numpy as np
import matplotlib.pyplot as plt
def run():
    trace=read(RUN/'results/calibration_candidates.json');rules=read(RUN/'protocol/frozen_H_rules.json');case='original_fit_cal_to_transfer';fig,axes=plt.subplots(1,3,figsize=(14,4.8))
    for ax,m in zip(axes,['H1','H2','H3']):
        rr=[r for r in trace if r['case_id']==case and r['method']==m and r['A']>0];sc=ax.scatter([100*r['A'] for r in rr],[100*r['R'] for r in rr],c=[r['wait_min'] for r in rr],cmap='viridis',s=30)
        chosen=next(r for r in rules if r['case_id']==case and r['method']==m)['calibration_summary'];ax.scatter([100*chosen['A']],[100*chosen['R']],marker='*',s=180,fc='none',ec='#bc3b36',lw=1.5,label='Frozen selected');ax.axhline(5,c='#a54b3b',ls=':',lw=1);ax.set(xlabel='Calibration source-equal A (%)',ylabel='Calibration source-equal R (%)',title=m+' | original cal26 / 7 sources');ax.legend(fontsize=8);ax.grid(alpha=.18);fig.colorbar(sc,ax=ax,label='Source-equal wait (min)',shrink=.7)
    fig.suptitle('Calibration diagnostics ONLY; no test candidate curve',fontsize=13);fig.tight_layout()
    save(fig,'B03_calibration_only_diagnostics','仅校准集：风险—覆盖—等待诊断','显示final校准26条/7来源的43候选；空采用候选R未定义不画点，原始CSV仍保留。其余14折完整候选在calibration_candidates。星号按事先排序选出，未用test风险配平。',['results/calibration_candidates.json','protocol/frozen_H_rules.json'])
