# Reproducible Minesweeper experiments

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
