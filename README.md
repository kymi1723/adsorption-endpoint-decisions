# Adsorption endpoint forecasting and sequential adoption

Reproducibility code, data and frozen models for *Learning when to stop adsorption kinetic measurements through selective endpoint forecasting*.
The explicitly supplied final main text and SI are fingerprinted in `provenance/manuscript_versions.json`. Original project files, manuscript Word files and frozen models were not overwritten. 

## Installation

Tested: Python **3.11.9**, NumPy **1.26.4**, SciPy **1.15.1**, scikit-learn **1.6.1**, joblib **1.4.2**, matplotlib **3.10.9**, threadpoolctl **3.5.0**, Pillow **11.1.0** on Windows. See `requirements-lock.txt` for all15 pinned runtime distributions. Other operating systems are not validated in this release.

Unzip, open a terminal in this directory, then:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python -m endpoint_release
```

On POSIX use `.venv/bin/python` instead. Installation is dependencies only; this source directory is the runnable package. `python /path/to/run_release.py ...` also works from another working directory. No project parent directory, AGENTS.md, original local paths or prior user cache is required. Python's standard library/interpreter and installed dependencies are required normally.

The local verification used an independent venv with **include-system-site-packages=false** and15 exact-version wheels recovered from the existing pip download cache, then installed using `pip --no-index --find-links ... -r requirements-lock.txt`. Network index attempts were cancelled without completed installs. The wheel source list is recorded locally; the public release does not depend on that cache or ship platform-specific dependency wheels. `pip check` passed. The default frozen route never retrains.

## Commands

All outputs must use a new directory; existing output directories are refused. Inputs and frozen models cannot be output destinations.

```powershell
# Default: freshly score with15 frozen trees, recalibrate U0-E, replay and score.
python -m endpoint_release evaluate --scheme U0-E --out outputs/frozen_U0_E

# Separate recorded original calibration: Figure2–5 and original SI protocol.
python -m endpoint_release evaluate --scheme Original_frozen --out outputs/original_protocol

# Full acceptance checks: headline counts, all U0-E metrics and3 real series.
python -m endpoint_release verify --out outputs/verification

# Rebuild16134 exhaustive states and15990 training rows from observations.
# The explicitly released PSO parameter cache is reused, never a hidden cache.
python -m endpoint_release build --out outputs/rebuilt

# Build, refit all15 tree heads once, recalibrate both protocols, evaluate.
python -m endpoint_release train --all-cases --out outputs/retrained

# Optional computationally heavier path: regenerate every PSO subset fit.
python -m endpoint_release train --all-cases --recompute-pso --out outputs/full_refit

# Without --all-cases, train refits only the final53-curve head and explicitly
# reuses14 frozen development heads. These are labelled in training_receipt.
python -m endpoint_release train --out outputs/final_head_only

# Three lab series, physically separate60min input files and90min diagnostics.
python -m endpoint_release laboratory --out outputs/laboratory

# New curve at60min, matching the laboratory source-exclusion configuration.
python -m endpoint_release predict examples/parallel_1_60min.json --configuration laboratory_source_excluded --out outputs/curve1

# General deployment uses common_U0_E by default; original_frozen is also explicit.
python -m endpoint_release predict examples/parallel_2_60min.json --configuration common_U0_E --out outputs/curve2

# All main/SI plots, numbered figures, table exports and plotting data.
python -m endpoint_release figures --out outputs/figures

# Recorded fixed-time, target and calibration-selected simple comparators.
python -m endpoint_release comparators --out outputs/fixed_comparators
```

`evaluate` also replays the recorded fixed-time/target comparators into clearly named additional files. U0-E never silently replaces their recorded clock calibration. `Simple_cal` uses the recorded calibration-only choice for each cost scenario; it is not reselected on test outcomes.

## New-curve input/output

Input JSON has `curve_id`, a **predeclared** `target_time_min`, `as_of_min`, `observations` (strictly increasing positive times and `value`), `scale`, and optional `next_time_min` from the intended schedule. At least3 observed points are required. The examples contain only the5 points through60min; no endpoint or later response is accepted. Unknown fields, duplicate/zero/nonfinite/future times are rejected. Do not put a full future trajectory into the inference payload.

`scale.response` is `fraction`, `removal_percent`, or `uptake_mg_g`. Uptake needs independently known positive `C0_mg_L` and `rho_g_L`; f=q*rho/C0. No curve endpoint/max or fitted capacity is used for normalization. The laboratory examples use C0=200mg/L and rho=2g/L. Response reversals are retained.

Outputs include the current target prediction in fraction (also mg/g for uptake), learned error score in pp, explicit threshold configuration, `adopt`/`continue`, first adopted state, original input times, per-prefix fits/features/scores, and requested next scheduled time if supplied. The score is an error regression, **not a probability**. Adoption refers to the first qualifying prefix, even if a caller later supplies additional observations. A continue action requests another actual scheduled measurement; this interface does not generate artificial measurements or optimize a new sampling clock.

## Data, models and protocols

- `data/`: normalized real observations and reading bounds, explicit family membership/normalization,98-curve training-task admission,130-curve evaluation paths, separated calibration/test targets, PSO parameter cache and D34–D38 laboratory files.
- `models/`:14 held-family heads and one distinct final head, with original model metadata and hashes. The final head fits53 curves/seven families. It does not produce every original79 prediction.
- `configs/`: fixed family partitions, tree recipe, PSO recipe, separate U0-E/original configurations, recorded fixed-time rules and scenario choices. Laboratory calibration excludes one Zheng family and uses25 curves/six families; literature calibration uses26/seven.
- `reference/`: original frozen scores/rules/data tables, exact supplied table text and figure media, and explicitly named plotting inputs. These are frozen comparison records, never overwritten by commands.
- `endpoint_release/`: CLI/IO wrappers and extracted original scientific/plotting functions; `tools/research_models/` contains original project modules copied unchanged.
- `validation/`: this round's actual verified receipts, selected numerical outputs and timings. Full retrained model files and bulky development outputs are retained in the local work directory, outside the public ZIP; users regenerate their own with `train`.
- `reproduced_figures/`:18 numbered figure units (6 main and12 SI, counting S8a/S8b separately). Fresh plot layouts are not claimed byte-identical to Word graphics. Exact supplied graphics are retained separately under `reference/final_manuscript_media/`.

See [reproduction_map.md](reproduction_map.md), [method_protocol.md](method_protocol.md), [verification_report.md](verification_report.md) and [manuscript_additions.md](manuscript_additions.md).

The benchmark retains130 scored curves/31 families/34 DOIs and a separate held metadata row in D1. D1 is not131 evaluated curves. Three parallel laboratory series form a separate single-system layer. Historical supporting analyses and alternative-model TableS9 are preserved under their own original designs, not relabelled as fresh U0-E ablations.

## Licence and GitHub publication

Original project code is licensed under the **[MIT License](LICENSE)**. See [LICENSE_SCOPE.md](LICENSE_SCOPE.md) for the covered source/documentation and the separate status of data, models, research records, manuscript materials and third-party dependencies. Their rights are not replaced by the code licence.

For GitHub, place this folder's **contents** at the repository root, including `README.md`, `LICENSE` and `.gitignore`. The sibling ZIP is the downloadable equivalent and may be attached as a Release asset. See [GITHUB_UPLOAD.md](GITHUB_UPLOAD.md).  Confirm applicable redistribution terms for non-code research assets before public posting. Publisher PDFs, original Word files, credentials, environments and unrelated history remain excluded.
