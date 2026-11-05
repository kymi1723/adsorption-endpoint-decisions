from .plot_support import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
def cost_grid():
    rows=read(RUN/'tables/T04_R2_minus_Simple_cost20.json');limit=max(abs(r['delta_J_pp']) for r in rows);limit=max(limit,.01);fig,axes=plt.subplots(3,2,figsize=(11,12),layout='constrained');images=[];data=[]
    for ax,bid,title in zip(axes.flat,ORDER,LABELS):
        rr=[r for r in rows if r['batch_id']==bid];arr=np.array([[next(r['delta_J_pp'] for r in rr if r['lambda_pp']==lam and r['mu_pp_per_min']==mu) for mu in [0.,.025,.05,.1]] for lam in [0.,.5,1.,2.,5.]])
        images.append(ax.imshow(arr,cmap='RdBu_r',norm=TwoSlopeNorm(0,-limit,limit),aspect='auto'));ax.set_xticks(range(4),['0','.025','.05','.1']);ax.set_yticks(range(5),['0','.5','1','2','5']);ax.set(xlabel='Scenario wait weight mu (pp/min)',ylabel='Scenario measurement weight lambda (pp)',title=title)
        for y in range(5):
            for x in range(4):ax.text(x,y,f'{arr[y,x]:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(arr[y,x])>.52*limit else '#152c3a')
        data+=rr
    fig.colorbar(images[0],ax=list(axes.flat),label='Source-equal cost difference R2 - Simple_cal (pp)',shrink=.7);save(fig,'F04_all20_cost_differences','六证据层全部20成本差','各批固定20格完整呈现；共用对称色标，不截断正差。λ是每新增一次测量的pp代价，μ是每等待一分钟的pp代价，均为研究情景权重而非已测经济价格，不是20独立试验；原original按各折cal的Simple映射，其他层用既定final规则，均不重选。*旧时钟边界批次需限制解释。',['tables/T04_R2_minus_Simple_cost20.json'],data=data)

def old_clock():
    rows=read(C01/'protocol/clock_boundary_inventory.json');rr=[r for r in rows if r['method']=='F_Last' and r['k']==7];n=read(N4/'results/fixed_clock_reading_diagnostic.json');r=.7499136705291377;fig,ax=plt.subplots(figsize=(10,5));plot=[]
    for row in rr:plot.append(dict(label=row['curve_id'].replace('Jiang2019_',''),center=row['center_ratio'],lower=row['ratio_lower'],upper=row['ratio_upper']))
    plot.append(dict(label='N4 real90/120 timebox',center=n['actual_native_ratio'],lower=n['reading_ratio_lower'],upper=n['reading_ratio_upper']))
    for i,p in enumerate(plot):ax.errorbar(p['center'],i,xerr=[[p['center']-p['lower']],[p['upper']-p['center']]],fmt='o',color='#47778b',capsize=3);ax.text(p['upper']+.001,i,f"{p['center']:.6f}",va='center',fontsize=8)
    ax.axvline(r,color='#a2463d',ls='--',label='Frozen r');ax.axvline(.75,color='#8d885f',ls=':',label='Nominal90/120');ax.set_yticks(range(len(plot)),[p['label'] for p in plot],fontsize=8);ax.invert_yaxis();ax.set(xlabel='Native last-time / target-time ratio; digitization reading interval',title='Earlier confirmation clock sensitivity (not a new rescore)');ax.legend(fontsize=9);ax.grid(axis='x',alpha=.2);fig.tight_layout();save(fig,'SF01_old_clock_boundary','旧N4/C01时钟边界单列','复用已保存区间，仅图示，不改变时钟、重选r或重评分。旧批固定对照受读图边界影响；本轮remaining03的136记录跨r为0，不能把两种状态混写。',[rel(C01/'protocol/clock_boundary_inventory.json'),rel(N4/'results/fixed_clock_reading_diagnostic.json')],folder='supplement',data=plot)
