# Exact implementation protocol

## Data and targets

f=q*rho/C0 for uptake; removal%=100f. Initial inventory comes from the recorded conditions, not endpoint values, full-curve maxima or fitted q_e. The PSO amplitude initial guess uses only the **current input maximum**, which is distinct from response normalization. Per-curve evidence is retained in `data/normalization_provenance.csv`, `data/development_curve_conditions.json` and D1. Unknown condition fields stay unknown.

The original98-curve nominal120 task admits a unique real point with graphical lower_time<=120<=upper_time. It forecasts that point's real central time, not an interpolated exact120 response. Inputs are real positive observations whose upper_time is strictly below the target's lower_time; t=0 never counts. The original admission additionally required at least4 such pretarget points. This historical admission constraint is retained even though a decision may begin at3 observations. Later layers retain their explicit task freezes; no target is selected by outcome. All98 original-task admission/exclusion geometry is shipped.

## Complete prefixes and nonconsecutive subsets

For a curve with m admitted pretarget points, fixed indices0,1,2 are always included. Enumerate integer masks0..2^(m−3)−1 in ascending order; bit j selects index3+j. Thus sizes3..m are represented with C(m−3,n−3) states of size n, **all** enumerated, no random sample, per-curve cap or subset seed. Original geometry had a50000-total-state preflight budget, not truncation; the admitted98 curves produce16134 states. The79 original curves contribute15990 valid PSO training rows. The final7-family fit uses14596 of these rows across53 curves. No test curve is used to train.

The parent removes the highest set bit, equivalently the latest included additional point. The initial3-point state has no parent. A continuous-prefix mask at count n is2^(n−3)−1. Calibration and evaluation use only complete prefixes k=3..m, with the original measured schedule. Nonconsecutive subsets remain in tree fitting, not skip-point deployment. All130 evaluation curves contribute750 recorded prefixes. State ID hashes retain the original task string, curve/input IDs and target ID/clock.

## PSO

The original `tools/research_models/prefix_budget.py` is copied unchanged. f(t)=fe*t/(tau+t); fit coordinates are (fe,log(tau)). SciPy `least_squares`, default method `trf`, default `jac='2-point'`, linear loss, x_scale1.0; fe∈[0,1], tau∈[1e−6,1e6]min; ftol=xtol=gtol=1e−11, max_nfev3000 **per start**. fe starts: clip(max(current f),.001,.9999), .9999. tau starts: max(1e−5,.1*t_first), median(current t),2*t_last. Cross in that loop order; retain success=True solutions and minimum prefix SSE, with original first-minimum tie handling. Original code relies on bounded SciPy finite residuals; no new optimizer/finite-solution filter is substituted. No target response enters any residual or initial guess. Failed fit remains unavailable; adoption still needs a finite available prediction and score.

All-state rebuilding defaults to the **explicit supplied parameter cache**, linked by regenerated state ID and independently reconstructed inputs. `--recompute-pso` regenerates the same six-start fits rather than consulting the cache; this full16134-fit option was not batch-run this round. Fresh laboratory fits did run without cached parameters.

## Features, parent error and labels

`endpoint_release/features.py::state_vector` is extracted with its body unchanged from the original20-feature implementation. Exact definitions are also in the supplied SI TableS1 export. Features1..20 are count, log1p(first/last clock), log(min/max query over last clock), last fraction, observed range, signed-log recent/overall dimensionless slopes, log1p(prefix RMSE pp), fe, log1p(tau/last), mean/range query prediction, log1p(RMS forecast-to-last gap pp), fe/tau boundary flags, fit-unavailable flag, log1p(latest parent prediction error pp), parent-available flag. For Q={T}, the min/max features coincide and query range=0; the frozen redundancy is preserved.

The newest-point check uses the **parent fit**, evaluated at the newly revealed last observation time. It is not current residual error or a target residual. It is available only when count>3 and a usable parent exists; otherwise the last two features are0,0. Current fit boundary flags use fe<=1e−6 or fe>=1−1e−6, and tau<=1.01e−6 or tau>=1e6/1.01. Unavailable-fit placeholders are exactly those in the original function and do not enable adoption.

Supervision is100*abs(current-input PSO target prediction − measured target fraction) pp, for valid original PSO states. No test target enters a feature. The original weight function recursively gives equal mass to canonical family, then curve, then observation count n, then equally among states left at that n. Weights sum to1 separately per fit. Family relations are shipped recorded equality/alias closure, never inferred from author-name resemblance.

## Trees and partition

ExtraTreesRegressor:128 trees, depth4, min_samples_leaf5, min_weight_fraction_leaf.01, max_features=float1.0, bootstrapFalse, criterion squared_error, random_state20261030, n_jobs4; remaining actual saved defaults are retained in each model metadata. No learned scaler/imputer. Finite negative predictions clip0; nonfinite scores unavailable.

The14 held-family folds each fit6 families, calibrate7 and test1, retaining recorded curve IDs/order. The distinct final model fits7 families/53 curves and calibrates7/26, tests19 transfer curves/six other families, then scores later layers unchanged. Partitions use the original SHA256 ranking with prefix `source_sequential_acceptance_calibration_v1|` on family labels; integer floor-half families fit and the remainder calibrate. `configs/folds.json` records the resulting authoritative allocation and hashes. No split search is performed. The laboratory branch excludes the Zheng family only from final calibration, leaving25 curves/six families; fit and model bytes unchanged.

## Calibration, availability and adoption

Common U0-E (Tables2–3): all distinct finite calibration-state scores with±infinity, complete first-adoption replay at each threshold; require A>0 and exact R<=1/20. Rank maximum exact A, minimum source-equal waiting, minimum observations, smaller threshold. No feasible adoption→all fallback. This spans the full score range. It is not the original limited learned search.

Original Learned: distinct finite scores in[0,5] plus5 and all-reject; require exact A>=1/4,R<=1/20; rank maximum A, minimum waiting, smaller threshold. Original H1–H3:41 linearly interpolated quantiles0:.025:1, deduplicate, add±infinity; require A>0,R<=1/20 and rank as U0-E. These original searches are separate from the principal common comparison. Actual quantile thresholds, including between-score values, are retained.

At each complete prefix use the first state whose prediction and score are available/finite and score<=c. No later correct prefix replaces an earlier adoption. H1=100*range(last3f)*(T−last_time)/(last_time−third_last_time); H2=100*abs(current target prediction−parent target prediction), k>=4; H3=expm1(feature19) with parent-available flag, k>=4. H2/H3 need the appropriate previous complete state. If none qualifies, acquire the actual target. Deployment can call the same process on currently revealed prefixes only.

`configs/common_U0_E.json`, `configs/original_frozen.json`, final model metadata and source-excluded laboratory config must not be mixed. Fold-specific thresholds remain fold-specific. The final learned threshold is2.1167078708551017pp. Laboratory H1/H2/H3 thresholds are.7008000078183579/.0019336565264982397/.10970778213584274pp. These differ from the original full-calibration H thresholds.

## Metrics and loss

Each curve has w_i=1/(K*n_family). A=sum(w*adopt), B=sum(w*adopt_and_error>5pp), R=B/A; zero adoption→undefined R, not0. Strict >5pp defines violation, no epsilon added to calibration/risk thresholds. Ordinary curve counts are separately reported. Conditional source-weighted MAE=all-population mean adopted error/A; ordinary adoption-only MAE is separate.

Time stops at the first adopted real observation or the measured target. Waiting=stop−third positive observation; total count includes initial3 and target on fallback. Fallback count=m+1, response error0 by replay definition. J=error_pp+lambda*(n−3)+mu*waiting, lambda={0,.5,1,2,5},mu={0,.025,.05,.1}; source-equal aggregate first, then an unweighted mean over20 preferences. Cells are not independent experiments. Advantage counts use delta<−1e−10; that is a display/comparison tie tolerance, not a5pp safety tolerance.

Original fixed-time comparators replay frozen r values, with no alternative state chosen after an unavailable planned fit. Simple_cal uses its frozen calibration-only per-scenario choice. Source-family resampling, tolerance and deletion figures consume the fully retained original uncertainty data: seed20261102,2000 whole-family draws with multiplicities, R recomputed as B/A, undefined draws retained. These graphics do not retrain models or turn descriptive percentiles into guarantees.
