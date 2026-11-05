# 建议补入正文/SI的方法文字（不直接修改Word）

以下据代码、冻结记录和本次实际运行核实；供作者选择并入最终稿。正文Tables2–3共同U0-E，原校准图/SI和实验排族配置必须继续分开。原创代码采用MIT；公开地址及非代码材料再分发范围未定，不虚构已公开。

## 正文2.3：求解细节

中文：PSO模型在(fₑ,logτ)坐标中通过SciPy least_squares的有界信赖域反射算法（trf，二点数值Jacobian、线性损失、x_scale=1.0）拟合。两个fₑ初值为clip(max f_prefix,0.001,0.9999)和0.9999，三个τ初值为max(10⁻⁵,0.1t₁)、输入时间中位数及2t_k，依原顺序交叉形成六个确定起点。fₑ及τ边界为[0,1]和[10⁻⁶,10⁶]min；三个收敛容差均为10⁻¹¹，每个起点最多3000次函数评估。在求解成功的候选中保留前缀残差平方和最小者。全部拟合残差、初值和特征仅使用当时已测数据及预先给定的目标时刻。

English: The PSO model was fitted in (fₑ, logτ) coordinates with SciPy's bounded trust-region reflective least_squares solver (trf, two-point numerical Jacobian, linear loss and x_scale=1.0). The two fₑ starts, clip(max f_prefix, 0.001, 0.9999) and 0.9999, were crossed in the recorded order with τ starts max(10⁻⁵,0.1t₁), median input time and 2t_k. Bounds were [0,1] for fₑ and [10⁻⁶,10⁶]min for τ; ftol, xtol and gtol were10⁻¹¹, with at most3000 function evaluations per start. The successful solution with the lowest prefix residual sum of squares was retained. Residuals, initializations and features used only the measurements then available and the specified target clock.

## 正文2.4：训练状态、父状态和校准区分

中文：对于具有m个合格目标前正时间观测的曲线，训练固定最早三点，并穷举其余m−3点的所有子集，生成2^(m−3)个状态（大小3至m），不进行随机抽样、数量截断或按预测效果筛选。父状态由删除当前子集的最后一个附加观测得到，因此最新点误差是父模型在该点时刻的预测与新揭示观测之差。初始三点状态没有可用父状态。全部曲线的特征构建完成后，拟合家族才通过100|p(T)−f(T)|标签训练误差评分器；样本权重依家族、曲线、观测数及该单元内状态逐层等分。校准和评价仅使用原网格的连续完整前缀。Tables2–3使用共同U0-E：穷举全部有限校准分数及±∞，在A>0、R≤0.05下按最大精确A、最小平均等待、最少观测、最小阈值选择。原始受限学习阈值搜索、原H分位阈值及实验排族U0-E分别保存，不相互代换。

English: For a curve with m eligible positive-time pretarget observations, fitting retained the earliest three and exhaustively enumerated all subsets of the remaining m−3 points, giving2^(m−3) states of sizes3 through m, without random sampling, truncation or performance-based selection. A state's parent omitted its last additional observation; the newest-point error therefore compared the parent model's prediction at that clock with the newly revealed response. The initial three-point state had no available parent. Fitting-family labels were100|p(T)−f(T)|, with weights divided equally by family, curve, observation count and the remaining states within that cell. Calibration and evaluation used complete consecutive prefixes on the original grid. Tables2–3 used common U0-E: all distinct finite calibration scores and±∞ were replayed, requiring A>0 and R≤0.05, then ordered by maximum exact A, minimum mean waiting, minimum observations and smaller threshold. The original restricted learned-score search, original heuristic quantile search and source-excluded laboratory U0-E configuration were retained separately.

## 正文2.7：可运行复现与计时

中文：本地发布副本保留测量值及图读区间、来源家族划分、六起点PSO、20维特征、15个冻结误差模型、阈值候选和首次采用流程，并提供冻结评价、从观测数据重建及重训、新曲线推理和图表生成入口。复现环境为Python3.11.9、NumPy1.26.4、SciPy1.15.1、scikit-learn1.6.1及joblib1.4.2，完整依赖锁定表随包提供。独立环境中重建的15990行训练特征/标签与原记录一致；15个模型按原配方各重训一次，在750个前缀上的最大评分差为7.11e-15pp，两个校准配置的首次动作保持相同。本次最终模型树拟合调用（含线程限制上下文管理）为0.1829s，单条五点前缀完整决策为0.2006s（含模型加载及三至五点PSO更新，不含程序导入或真实测量）；原历史计时因包含保存或不同校准范围而单列，不与新计时互换。商业CPU型号未核实，不填入推测型号。

English: The local release preserves observations and graphical reading intervals, source-family partitions, six-start PSO fitting, the20-feature representation,15 frozen error-score models, calibration candidates and first-adoption replay. Separate commands support frozen evaluation, sample reconstruction and retraining, new-curve inference, and figure/table generation. The verified environment used Python3.11.9, NumPy1.26.4, SciPy1.15.1, scikit-learn1.6.1 and joblib1.4.2, with a complete dependency lockfile. The reconstructed15,990 training feature/label rows matched the archived records. Refitting each of the15 heads once under its original recipe changed scores across750 prefixes by at most7.11e-15pp and preserved first actions under both calibration configurations. In this run, fitting the final tree head, including threadpool-limit context entry/restoration, took0.1829s and one complete five-observation decision took0.2006s, including model loading and the three- to five-point PSO updates but excluding interpreter imports and laboratory measurement. Historical timings are reported separately because their serialization and calibration scopes differ. A commercial CPU model was not verified and is not inferred.

## SI S3：完整规则及训练规模

中文：状态生成按升序位掩码记录，位j代表第四个及以后的第j个合格观测；父掩码移除最高有效位。完整前缀的掩码为2^(k−3)−1。原98曲线名义120min任务共有16134个状态，原79曲线贡献15990个有效训练行；最终53曲线/七家族拟合含14596行。训练行是同一曲线的衍生观测状态，不视为独立实验。零时点不计入前三点；目标由唯一覆盖名义120min的原测量时间区间确定，预测使用其真实中心时刻，无插值生成目标。拟合/校准/评价家族及对应DOI隔离遵循随包冻结清单。缺失拟合和评分保留不可用状态，未用后期响应补值。包内明确参数缓存用于快速重建；可选全PSO重拟合入口与独立重训输出分开，本轮不声称已重跑全部历史PSO优化。

English: States were generated in ascending bit-mask order, with each bit selecting an eligible observation after the first three; the parent removed the highest set bit. The complete-prefix mask at count k was2^(k−3)−1. The98-curve nominal120-min task contained16,134 states; the79 original curves supplied15,990 valid fitting rows, of which14,596 belonged to the final53-curve/seven-family fit. These rows are derived states, not independent experiments. Zero time did not count toward the initial three. A unique real observation whose reading-time interval contained nominal120min defined the target, and its measured central clock was queried without interpolation. Source-family and DOI separation followed the released frozen partitions. Unavailable fits/scores remained unavailable and were not imputed with later responses. The explicitly shipped parameter cache supports fast reconstruction; optional full PSO refitting and tree-retraining outputs are separate, and this verification does not assert that all historical PSO optimizations were rerun.

## Data and code availability：当前可用表述及发布后待替换项

中文：支持本文的衍生曲线数据、来源/家族及拟合—校准—评价清单、冻结模型、运行代码、作图数据和复现说明已整理为本地可运行的adsorption_endpoint_release发布候选。主表共同U0-E、原始校准及实验排族配置分别标注。项目原创代码采用MIT许可证，适用范围及第三方例外随包说明；数据、模型及论文图表不自动适用MIT。公开存储位置将在确认非代码材料再分发范围并完成发布后提供；当前不声明已存在远程仓库或永久标识。出版方原文材料保留各自权利，不随本包分发或重新授权。

English: Derived curve data, source/family and fitting–calibration–evaluation manifests, frozen models, runnable code, plotting data and reproduction instructions have been assembled as the local adsorption_endpoint_release candidate. Common U0-E main-table results, original-calibration results and the source-excluded laboratory configuration are explicitly distinguished. The original project code is licensed under MIT, with its scope and third-party exceptions documented in the release. Data, model artefacts and manuscript figures are not automatically covered by that code licence. The public location will be provided after the applicable non-code redistribution terms are confirmed and release is completed; no remote repository or persistent identifier is currently asserted. Original publisher materials retain their respective rights and are neither redistributed nor relicensed in this package.

作者后续实际公开后，应将上述待定句替换为**真实仓库/归档地址、版本标记、代码MIT及实际非代码许可说明、持久标识（若确有）**。不要提前填造占位URL或声称已开放。
