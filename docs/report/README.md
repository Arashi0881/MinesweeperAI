# Reproducible Minesweeper experiments

The updated Vietnamese report is available in
[reports/Bao_cao_Minesweeper_AI_cap_nhat_thuc_nghiem.docx](reports/Bao_cao_Minesweeper_AI_cap_nhat_thuc_nghiem.docx),
with report update and structure audits beside it. The validated full dataset
is [data/full_20261011](data/full_20261011). Word pagination was not rendered;
update the table of contents and page numbers in Word before submission.

These scripts generate the raw data, tables, and figures used by the report.
They resolve the repository root from their own location, so the commands do
not depend on the current working directory.

## Setup

The experiment runner and summarizer use the Python standard library. Plotting
requires matplotlib:

```powershell
python -m pip install matplotlib
```

The project test dependencies remain available through the existing `pytest`
setup. The scripts were written for Python 3.11 or newer.

## Run experiments

A small smoke run:

```powershell
python docs/report/scripts/run_experiments.py `
  --suite main `
  --games 5 `
  --out-dir docs/report/data/smoke_001
```

The full suite uses the sample sizes defined in the experiment specification:

```powershell
python docs/report/scripts/run_experiments.py `
  --suite all `
  --out-dir docs/report/data/run_001
```

`--out-dir` is required and must be empty or absent. Existing output is never
overwritten. Use a new directory for every run. Seeds for game `i` are
`seed_start + i`; `--seed-start` defaults to `0`.

Available suites are `all`, `main`, `first-click`, `density`, `flood-fill`,
`corner`, and `outside`. `--games N` overrides the sample size for smoke runs.
When `all` is used, identical configurations shared between groups are run
once and referenced by multiple group names in the manifest.

Each experiment writes one CSV row after every completed game and flushes the
file. The CSV contains the existing `GameRecord` fields plus:

- `experiment_id`
- `opening_strategy`
- `include_outside`

`guesses` counts moves with `certain=False`. Under `UNSAFE`, the opening move
is currently marked certain and is therefore not counted as a guess.

## Summarize

```powershell
python docs/report/scripts/summarize_results.py `
  --data-dir docs/report/data/run_001
```

The summarizer validates the manifest, CSV schema, expected row counts, result
values, duplicate seeds, and complete seed ranges. It refuses to create the
official tables from an interrupted run.

It writes:

- `summary.csv`: one row per complete configuration.
- `tables.md`: tables for solver/preset, first-click rules, density, flood fill,
  center/corner, outside-frontier, and LV3 timing.

Wilson 95% intervals use the existing `wilson_interval` implementation. The
95th percentile uses linear interpolation at position `(n - 1) * q`; this is
the fixed method used for all timing summaries. Times are in milliseconds.

## Plot

```powershell
python docs/report/scripts/plot_results.py `
  --data-dir docs/report/data/run_001
```

Figures are written to `figures/` as both 300 DPI PNG and SVG:

- `win_rate_by_solver`: grouped solver bars by preset with Wilson intervals.
- `win_rate_by_density`: LV3 win rate against actual mine density with Wilson
  intervals.

The intended report mapping is `win_rate_by_solver` to Figure 4.1 and
`win_rate_by_density` to Figure 4.2. Missing groups are reported instead of
being filled with guessed values.

## Manifest and interpretation limits

`manifest.json` records the schema version, Git commit, working-tree state,
Python executable/version, OS, CPU when available, timestamps with timezone,
command line, and every configuration's expected/completed counts and CSV
path. When the working tree is dirty, the run should be associated with the
working-tree patch saved beside the data by the runner.

The same seed only guarantees the same board when board-generation rules and
the opening cell are the same. Center/corner and `SAFE`/`OPENING` variants can
therefore generate different boards for the same seed. Timing depends on the
machine and environment. `stalled` may represent a solver stop, an illegal
move, an exception, or the batch move limit. Confidence intervals describe
sampling uncertainty; overlapping Wilson intervals alone are not a statistical
significance test.

## Verified cloud workflow and sample reuse

From the checkout root on Linux/macOS:

```bash
export UV_CACHE_DIR=/workspace/.cache/uv  # cloud home cache is read-only
uv sync --locked --extra report
uv run --no-sync pytest -q
uv run --no-sync python docs/report/scripts/run_experiments.py --suite all --games 5 --out-dir docs/report/data/smoke_new
uv run --no-sync python docs/report/scripts/summarize_results.py --data-dir docs/report/data/smoke_new
MPLCONFIGDIR=/workspace/.cache/matplotlib uv run --no-sync python docs/report/scripts/plot_results.py --data-dir docs/report/data/smoke_new
```

Use a **new** output directory for the full run and omit `--games`:

```bash
uv run --no-sync python docs/report/scripts/run_experiments.py --suite all --out-dir docs/report/data/run_new
uv run --no-sync python docs/report/scripts/summarize_results.py --data-dir docs/report/data/run_new
MPLCONFIGDIR=/workspace/.cache/matplotlib uv run --no-sync python docs/report/scripts/plot_results.py --data-dir docs/report/data/run_new
```

Absolute script and output paths also work from another directory. No display,
credentials, or running services are required. Plotting is headless. The cloud
run uses Python 3.12.14; the uv environment locks matplotlib 3.11.2.

| Group | Configurations | Games per configuration |
|---|---|---:|
| main | random/lv1/lv2/lv3 × 5×5–3, 9×9–10, 16×16–40 | 1,000 |
| main | same solvers × 16×30–99 | 300 |
| first-click | lv3 9×9–10 × OPENING/SAFE/UNSAFE | 1,000 |
| density | lv3 9×9 × 5–24 integer mines, inclusive | 500 |
| flood-fill | lv3 9×9–10 × BFS/DFS | 1,000 |
| corner | lv3 9×9–10 × center/corner × SAFE/OPENING | 1,000 |
| outside | lv3 9×9–10 and 16×16–40 × False/True | 1,000 |
| outside | lv3 16×30–99 × False/True | 300 |

Defaults are OPENING, chord enabled, BFS, center opening, outside=False.
Random retains its random first move, recorded as `opening_strategy=random`.
The all suite contains **43 unique configurations and 30,000 distinct game
records**. A shared CSV holds the largest requested sample, not a sum of
requests. For 9×9–10 LV3 baseline it holds 1,000 seeds; the density table uses
only its first 500 seeds. `group_games` records these distinct sample sizes.
The density baseline overlaps the main sample and is not independent.

The summarizer additionally writes `group_summary.csv`: group-specific views
retaining each requested seed prefix. Plots read these views, all computed
from validated CSVs, to preserve the 500-game density sample. They refuse
incomplete solver grids or missing density points. Solver hatches supplement
colors; titles give sample sizes and rules.

`mean_safe_coverage` is the arithmetic mean of
`cells_revealed / (rows * cols - mines)` over games;
`stalled_safe_coverage` restricts that mean to stalled games and is empty when
there are none. No mine cell is counted as revealed by this metric. Tables
include moves, guesses, coverage and mean/median/p95/max times.

Raw CSV keeps all GameRecord fields: seed, rows, cols, mines, density,
first_click, chord, flood_fill, solver, result, moves, guesses, cells_revealed,
mines_remaining, cells_remaining and time_ms, plus the three experiment fields
described above. Raw density follows GameRecord's four-decimal rounding;
summary density is computed from integer mines and dimensions. Time follows
the engine's three-decimal ms recording; statistics apply no further rounding
before calculation.

| Report section | Group / output |
|---|---|
| 4.2.1 and Figure 4.1 | main, win_rate_by_solver.png/.svg |
| 4.2.2 | first-click |
| 4.2.3 and Figure 4.2 | density, win_rate_by_density.png/.svg |
| 4.2.4 | flood-fill |
| 4.2.5 opening position | corner |
| 4.2.5 frontier candidates | outside |
| 4.2.6 whole-game LV3 timing | main, restricted to lv3 |
| 4.3 safe-cell progress | main, coverage columns |

Schema 2 records suite, seed start, games override, group sample sizes, CSV
SHA-256 checksums, and source SHA-256 hashes. `source_snapshot.zip` preserves
the Python application and experiment scripts actually used, including
untracked Python files; `working_tree.patch` preserves tracked edits. Output
files can make the working tree dirty without changing solver code.
Summarization checks the planned matrix, snapshot/CSV hashes, per-row
configuration, seed ranges and basic numeric invariants. Do not use interrupted
runs as official results or append their samples to another run.

The uploaded report's numbers remain historical until reconciled with a
complete validated run. `docs/HEURISTICS.md` describes a separate 200-game
sample and must not be merged into this dataset. Replication compares outcomes,
moves, guesses and revealed cells, excluding time_ms.

Ablation of Degree Heuristic/propagation/INFO, DFS node/prune/depth statistics,
independent brute-force validation, and significance tests remain outside this
spec. Win rates alone establish none of those. Coverage is descriptive and
changes neither solvers nor gameplay.
