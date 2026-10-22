#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(encoding="utf-8") as handle:
        return list(csv.reader(handle))


def normalize(cell: str):
    cell = cell.strip()
    if cell == "":
        return None
    try:
        value = float(cell)
        return round(value, 8)
    except ValueError:
        return cell.lower()


def compare(expected: Path, actual: Path) -> list[str]:
    exp = read_csv(expected)
    act = read_csv(actual)
    errors = []
    if len(exp) != len(act):
        errors.append(f"número de linhas: esperado {len(exp)}, obtido {len(act)}")
    for r, (erow, arow) in enumerate(zip(exp, act), start=1):
        if len(erow) != len(arow):
            errors.append(f"linha {r}: número de colunas esperado {len(erow)}, obtido {len(arow)}")
            continue
        for c, (e, a) in enumerate(zip(erow, arow), start=1):
            if normalize(e) != normalize(a):
                errors.append(f"linha {r}, coluna {c}: esperado {e!r}, obtido {a!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara os CSV produzidos com os valores da tese.")
    parser.add_argument("--results", type=Path, default=ROOT / "results")
    args = parser.parse_args()

    pairs = [
        (ROOT / "expected_results" / "table3_classical_nuclear_5.csv", args.results / "classical" / "classical_nuclear_5_states.csv"),
        (ROOT / "expected_results" / "table4_classical_cuban_12.csv", args.results / "classical" / "classical_cuban_missile_crisis_12_states.csv"),
        (ROOT / "expected_results" / "table5_lh_nuclear_5.csv", args.results / "limited_horizon" / "lh_nuclear_5_states.csv"),
        (ROOT / "expected_results" / "table6_lh_cuban_12.csv", args.results / "limited_horizon" / "lh_cuban_missile_crisis_12_states.csv"),
        (ROOT / "expected_results" / "table7_maximin_nuclear_5.csv", args.results / "maximin" / "nuclear_5_states" / "maximin.csv"),
        (ROOT / "expected_results" / "table8_maximin_focal_credible_nuclear_5.csv", args.results / "maximin" / "nuclear_5_states" / "focal_credible.csv"),
        (ROOT / "expected_results" / "table9_maximin_opponent_credible_nuclear_5.csv", args.results / "maximin" / "nuclear_5_states" / "opponent_credible.csv"),
        (ROOT / "expected_results" / "table10_maximin_total_credible_nuclear_5.csv", args.results / "maximin" / "nuclear_5_states" / "total_credible.csv"),
        (ROOT / "expected_results" / "table11_maximin_indifference_nuclear_5.csv", args.results / "maximin" / "nuclear_5_states" / "indifference.csv"),
    ]
    checked = 0
    failed = 0
    for expected, actual in pairs:
        if not actual.exists():
            print(f"SKIP: {actual} ainda não existe")
            continue
        checked += 1
        errors = compare(expected, actual)
        if errors:
            failed += 1
            print(f"FAIL: {actual}")
            for error in errors[:20]:
                print(f"  - {error}")
        else:
            print(f"OK: {actual}")
    if checked == 0:
        print("Nenhum resultado encontrado para verificar.")
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
