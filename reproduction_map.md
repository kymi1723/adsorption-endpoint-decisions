# Reproduction map

Version basis: the two explicitly supplied integrated Word files + their model SHA + saved partitions/recipes/selected actions. No directory timestamps were used.

|Paper item|Code/data/configuration|Protocol / boundary|
|---|---|---|
|Main Table1|`data/evaluation_curves.json; configs/folds.json; final_table_exports/main_table_01.csv`|Recorded6 layers and fit/cal roles; no pooling|
|Main Table2|`evaluation.evaluate; common_U0_E.json; policy_layer_metrics.json`|Fresh frozen/tree or retrained U0-E, 5pp, no family deletion|
|Main Table3|`evaluation.evaluate; scenario_wins.json; scenario20.json`|Same U0-E rules as Table2, Learn−H1,20 fixed weights|
|Figure1|`plot_original.py; configs/folds.json`|Role/workflow schematic; original body reused|
|Figures2–5|`plot_original.py; reference/plot_inputs/T01_all_method_comparison.json, ST03_R2_minus_H_family_mean20.json, T03_R2_minus_H_cost20.json, F05_representative_case_data.json`|Original_frozen only; original14-fold/final policies; retained failures|
|Figure6|`figures.py; data/laboratory/D34,D36,D38`|New layout from3 supplied parallel series; freshly verified numerical forecasts|
|SI FigureS1|`plot_calibration.py; calibration_candidates.json; original_H_rules.json`|Original calibration candidates; no test candidate scan|
|SI FigureS2|`plot_archived_si.old_clock; clock_boundary_inventory.json; fixed_clock_reading_diagnostic.json`|Archived clock-reading intervals; no new threshold selection|
|SI FigureS3|`plot_archived_si.cost_grid; T04_R2_minus_Simple_cost20.json; configs/simple_cal_choices.json`|Original frozen20-scenario simple comparator|
|SI FiguresS4–S7|`plot_sensitivity.py; reference/paper_tables/T01,T09,T14; selected_rules.json`|Both original and explicitly named uniform/tolerance/deletion branches|
|SI FiguresS8a/S8b|`plot_learning.py; score_distribution_by_m.json; policy_distribution_by_m.json`|Original127 source-subset diagnostic summaries, not rerun/retuned|
|SI FigureS9|`plot_observation_budget.py; sampling_paired_scores.json`|Earlier nested-failure-constrained correction,86 curves, terminal-three targets; not current PSO/R2 ablation|
|SI FigureS10|`plot_agreement.py; case_evidence_layers.json`|Original fixed Fan/Du PSO/PFO/Last forecasts; future points only retrospective|
|SI FigureS11|`figures.py; laboratory D36,D38`|Three-series source-excluded U0-E scores;90min post-decision diagnostic|
|SI TablesS1–S5|`final_table_exports; feature/state and original/uniform rules; reference/paper_tables`|S1 exact20-feature dictionary; S2 original protocol; S3 common variants; S4 conceptual CBES comparison; S5 original loss|
|SI TablesS6–S8/S7a|`laboratory D34–D38; inference.laboratory; final_table_exports`|27 real values, mean/sample SD/RSD,12 fits,15 actions; target truths separate|
|SI TableS9|`final_table_exports/SI_table_14.csv; manuscript_versions.json`|Exact supplied four-alternative summary; historical comparisons retained, not reproduced as new trainings|


Run `python -m endpoint_release figures --out outputs/figures`: `paper_numbered/` has18 figure units, `paper_tables/` has full-precision principal tables and exact supplied table text; `plot_data/` holds every plotting input. `figure_number_map.csv` is the generated file map. Main Tables2–3 numerical recalculation is in the separate `evaluate --scheme U0-E` results. Original figures must not be relabelled U0-E.

All D1–D33 files resolve through `reference/paper_tables/supplementary_data_directory.json`: its historical paths are provenance strings; actual release files are the matching basename under `reference/paper_tables/` or `/original/`. D34–D38 are in `data/laboratory/`. Original/robustness namespaces remain separate. The original directory file is not used as a runtime path resolver.

Exact final Word media (PNG/SVG) are under `reference/final_manuscript_media/main` and `/SI`, with document/member/SHA in `provenance/final_figure_media.json`. Fresh plots reuse existing project plotting implementations and the final laboratory numerical files; they are **not asserted to recreate the integrated Word graphic styling byte-for-byte**. The particular editing source used to restyle all final embedded graphics was not supplied/identified. Exact media extraction and data-based figure generation are distinctly labelled.

The source-subset/PFX/E5/M2/Z0 comparison trainings belong to historical supporting designs, not the final frozen estimator training recipe. Their manuscript-reported summary tables and plot data are supplied; this release does not falsely claim that the optional main-model retraining reproduces every alternative-development training. Original unchanged-data provenance and precise current scope are retained.
