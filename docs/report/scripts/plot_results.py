"""Plot experiment summaries into PNG and SVG figures."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _read_summary(data_dir: Path) -> list[dict[str, str]]:
    path = data_dir / "summary.csv"
    if not path.exists():
        raise ValueError(f"missing summary: {path}; run summarize_results.py first")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _save(figure, output: Path, name: str) -> None:
    figure.savefig(output / f"{name}.png", dpi=300, bbox_inches="tight")
    figure.savefig(output / f"{name}.svg", bbox_inches="tight")


def plot_solver(rows: list[dict[str, str]], output: Path) -> bool:
    main = [row for row in rows if "main" in row["groups"]]
    if not main:
        return False
    import matplotlib.pyplot as plt

    presets = sorted({f"{row['rows']}x{row['cols']}" for row in main})
    solvers = sorted({row["solver"] for row in main})
    values = defaultdict(dict)
    intervals = defaultdict(dict)
    for row in main:
        preset = f"{row['rows']}x{row['cols']}"
        values[preset][row["solver"]] = float(row["win_rate"]) * 100
        intervals[preset][row["solver"]] = (
            float(row["win_rate"]) * 100 - float(row["ci_low"]) * 100,
            float(row["ci_high"]) * 100 - float(row["win_rate"]) * 100,
        )
    figure, axis = plt.subplots(figsize=(10, 6))
    width = 0.8 / len(solvers)
    positions = list(range(len(presets)))
    for index, solver in enumerate(solvers):
        heights = [values[preset].get(solver, 0) for preset in presets]
        errors = [intervals[preset].get(solver, (0, 0)) for preset in presets]
        axis.bar(
            [position + index * width for position in positions],
            heights,
            width,
            label=solver,
            yerr=list(zip(*errors)) if errors else None,
            capsize=3,
        )
    axis.set_title("Win rate by solver and preset")
    axis.set_xlabel("Preset dimensions")
    axis.set_ylabel("Win rate (%)")
    axis.set_ylim(0, 100)
    axis.set_xticks([position + width * (len(solvers) - 1) / 2 for position in positions], presets)
    axis.legend(title="Solver")
    figure.tight_layout()
    _save(figure, output, "win_rate_by_solver")
    plt.close(figure)
    return True


def plot_density(rows: list[dict[str, str]], output: Path) -> bool:
    density = [
        row for row in rows
        if "density" in row["groups"] and row["solver"] == "lv3"
    ]
    if not density:
        return False
    import matplotlib.pyplot as plt

    density.sort(key=lambda row: float(row["density"]))
    x = [float(row["density"]) * 100 for row in density]
    y = [float(row["win_rate"]) * 100 for row in density]
    low = [float(row["ci_low"]) * 100 for row in density]
    high = [float(row["ci_high"]) * 100 for row in density]
    figure, axis = plt.subplots(figsize=(9, 6))
    axis.plot(x, y, marker="o", label="LV3")
    axis.fill_between(x, low, high, alpha=0.2, label="95% Wilson CI")
    axis.set_title("LV3 win rate by actual mine density")
    axis.set_xlabel("Mine density (%)")
    axis.set_ylabel("Win rate (%)")
    axis.set_ylim(0, 100)
    axis.legend()
    figure.tight_layout()
    _save(figure, output, "win_rate_by_density")
    plt.close(figure)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        rows = _read_summary(args.data_dir)
        output = args.data_dir / "figures"
        output.mkdir(exist_ok=True)
        produced = []
        if plot_solver(rows, output):
            produced.append("win_rate_by_solver")
        if plot_density(rows, output):
            produced.append("win_rate_by_density")
        if not produced:
            raise ValueError("no complete data groups available for plotting")
    except (OSError, ValueError, ImportError) as exc:
        parser.error(str(exc))
    print(f"wrote figures: {', '.join(produced)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
