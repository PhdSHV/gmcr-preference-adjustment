#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gmcr_adjustment.instances import get_instance
from gmcr_adjustment.models import custo_Lh


def parse_states(value: str, upper: int) -> list[int]:
    if value.lower() == "all":
        return list(range(upper))
    states = []
    for token in value.split(","):
        state = int(token.strip())
        if not 1 <= state <= upper:
            raise argparse.ArgumentTypeError(f"Estado fora do intervalo 1..{upper}: {state}")
        states.append(state - 1)
    return sorted(set(states))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduz os resultados da estabilidade de horizonte limitado L_h.")
    parser.add_argument("--instance", default="5", help="5/nuclear ou 12/cuban")
    parser.add_argument("--max-horizon", type=int, default=None)
    parser.add_argument("--states", default="all")
    parser.add_argument("--solver", choices=["auto", "cbc", "cplex"], default="auto")
    parser.add_argument("--solver-log", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "limited_horizon")
    parser.add_argument("--no-plot", action="store_true", help="não gerar gráfico PNG")
    args = parser.parse_args()

    instance = get_instance(args.instance)
    max_h = args.max_horizon or (15 if instance.states == 5 else 6)
    states = parse_states(args.states, instance.states)
    files = instance.files
    args.output.mkdir(parents=True, exist_ok=True)

    rows = []
    for state in states:
        costs = []
        for horizon in range(1, max_h + 1):
            cost = custo_Lh(
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
            value = None if cost is None else float(cost)
            costs.append(value)
            print(f"L_h estado={state+1:2d} h={horizon:2d} custo={value}")
        rows.append([state + 1, *costs])

    path = args.output / f"lh_{instance.key}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["state", *[f"h={h}" for h in range(1, max_h + 1)]])
        writer.writerows(rows)

    if not args.no_plot:
        horizons = list(range(1, max_h + 1))
        plt.figure(figsize=(10, 6))
        for row in rows:
            plt.plot(horizons, row[1:], marker="o", label=f"Estado {row[0]}")
        plt.xlabel("Horizonte")
        plt.ylabel("Custo ótimo")
        plt.title(f"Estabilidade L_h - {instance.key}")
        plt.xticks(horizons)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(args.output / f"lh_{instance.key}.png", dpi=300)
        plt.close()

    print(f"Resultados salvos em {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
