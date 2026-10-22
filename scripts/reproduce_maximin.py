#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys

import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gmcr_adjustment.instances import get_instance
from gmcr_adjustment.models import (
    custo_maxmin,
    custo_maxmin_credivel,
    custo_maxmin_indiferenca,
    custo_maxmin_oponente_credivel,
    custo_maxmin_total_credivel,
)

CRITERIA = {
    "maximin": custo_maxmin,
    "focal_credible": custo_maxmin_credivel,
    "opponent_credible": custo_maxmin_oponente_credivel,
    "total_credible": custo_maxmin_total_credivel,
    "indifference": custo_maxmin_indiferenca,
}


def parse_selection(value: str, upper: int) -> list[int]:
    if value.lower() == "all":
        return list(range(upper))
    result = []
    for token in value.split(","):
        state = int(token.strip())
        if state < 1 or state > upper:
            raise argparse.ArgumentTypeError(f"Estado fora do intervalo 1..{upper}: {state}")
        result.append(state - 1)
    return sorted(set(result))


def normalize(result):
    if isinstance(result, tuple):
        cost = result[0] if len(result) > 0 else None
        status = result[1] if len(result) > 1 else "Unknown"
        preferences = result[2] if len(result) > 2 else None
        return cost, status, preferences
    return result, "Optimal" if result is not None else "Unknown", None


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduz a família de modelos Maximin.")
    parser.add_argument("--instance", default="5", help="5/nuclear ou 12/cuban")
    parser.add_argument("--max-horizon", type=int, default=None)
    parser.add_argument("--states", default="all", help="all ou estados 1-based separados por vírgula")
    parser.add_argument("--criteria", default="all", help="all ou nomes separados por vírgula")
    parser.add_argument("--solver", choices=["auto", "cbc", "cplex"], default="auto")
    parser.add_argument("--solver-log", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "maximin")
    parser.add_argument("--no-plots", action="store_true", help="não gerar gráficos PNG")
    args = parser.parse_args()

    instance = get_instance(args.instance)
    max_h = args.max_horizon or (15 if instance.states == 5 else 6)
    if max_h < 1:
        parser.error("--max-horizon deve ser positivo")
    states = parse_selection(args.states, instance.states)

    if args.criteria.lower() == "all":
        criteria = list(CRITERIA)
    else:
        criteria = [x.strip() for x in args.criteria.split(",")]
        unknown = [x for x in criteria if x not in CRITERIA]
        if unknown:
            parser.error(f"Critérios desconhecidos: {', '.join(unknown)}")

    files = instance.files
    output_dir = args.output / instance.key
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    plot_data = {state: {} for state in states}

    for criterion in criteria:
        function = CRITERIA[criterion]
        rows = []
        summary[criterion] = {}
        for state in states:
            costs = []
            summary[criterion][str(state + 1)] = {}
            for horizon in range(1, max_h + 1):
                result = function(
                    H=horizon,
                    S=instance.states,
                    N=2,
                    s=state,
                    arquivo_J1=str(files["J1"]),
                    arquivo_J2=str(files["J2"]),
                    arquivo_P1=str(files["P1"]),
                    arquivo_P2=str(files["P2"]),
                    solver=args.solver,
                    msg=args.solver_log,
                )
                cost, status, preferences = normalize(result)
                value = None if cost is None else float(cost)
                costs.append(value)
                summary[criterion][str(state + 1)][str(horizon)] = {
                    "cost": value,
                    "status": status,
                    "W": preferences,
                }
                print(f"{criterion:20s} estado={state+1:2d} h={horizon:2d} status={status} custo={value}")
            rows.append([state + 1, *costs])
            plot_data[state][criterion] = costs

        csv_path = output_dir / f"{criterion}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["state", *[f"h={h}" for h in range(1, max_h + 1)]])
            writer.writerows(rows)

    (output_dir / "details.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if not args.no_plots:
        horizons = list(range(1, max_h + 1))
        for state, criterion_data in plot_data.items():
            plt.figure(figsize=(10, 6))
            for criterion in criteria:
                plt.plot(horizons, criterion_data[criterion], marker="o", label=criterion)
            plt.xlabel("Horizonte")
            plt.ylabel("Custo ótimo")
            plt.title(f"Família Maximin - estado {state + 1} - {instance.key}")
            plt.xticks(horizons)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=8)
            plt.tight_layout()
            plt.savefig(output_dir / f"state_{state + 1}.png", dpi=300)
            plt.close()

    print(f"Resultados salvos em {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
