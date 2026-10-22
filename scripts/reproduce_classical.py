#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gmcr_adjustment.instances import get_instance

SOURCES = {
    "nash": "TESE - Preferências transitivas - Algoritmo Nash  - SOLUCAO.py",
    "gmr": "TESE - Preferências transitivas - Algoritmo GMR  - SOLUCAO.py",
    "smr": "TESE - Preferências transitivas - Algoritmo SMR - SOLUCAO.py",
    "seq": "Preferências transitivas - Algoritmo SEQ - SOLUÇÃO.py",
    "sseq": "TESE - Preferências transitivas - Algoritmo SSEQ - SOLUCAO.py",
}


def parse_states(value: str, upper: int) -> list[int]:
    if value.lower() == "all":
        return list(range(upper))
    result = []
    for token in value.split(","):
        state = int(token.strip())
        if not 1 <= state <= upper:
            raise argparse.ArgumentTypeError(f"Estado fora do intervalo 1..{upper}: {state}")
        result.append(state - 1)
    return sorted(set(result))


def patched_source(text: str, states: int, focal_state: int, solver: str) -> str:
    text = re.sub(r"S\s*=\s*set\(range\(\d+\)\)", f"S = set(range({states}))", text, count=1)
    text = re.sub(r"(?m)^s\s*=\s*\d+.*$", f"s = {focal_state}  # Estado focal (0-based)", text, count=1)
    text = re.sub(r"([JP][12])-\d+est\.csv", rf"\1-{states}est.csv", text)
    if solver == "cbc":
        text = text.replace("from pulp import ", "from pulp import PULP_CBC_CMD, ", 1)
        text = text.replace("model.solve()", "model.solve(PULP_CBC_CMD(msg=False))", 1)
    elif solver == "cplex":
        text = text.replace("from pulp import ", "from pulp import CPLEX_CMD, ", 1)
        text = text.replace("model.solve()", "model.solve(CPLEX_CMD(msg=False))", 1)
    return text


def run_one(criterion: str, instance, state: int, solver: str, timeout: int):
    source_path = ROOT / "legacy" / "original_sources" / SOURCES[criterion]
    text = source_path.read_text(encoding="utf-8-sig")
    text = patched_source(text, instance.states, state, solver)

    with tempfile.TemporaryDirectory(prefix="gmcr_classical_") as tmp_name:
        tmp = Path(tmp_name)
        for key, src in instance.files.items():
            shutil.copy2(src, tmp / f"{key}-{instance.states}est.csv")
        script = tmp / f"run_{criterion}.py"
        script.write_text(text, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, script.name], cwd=tmp, text=True,
            capture_output=True, timeout=timeout
        )
        reports = list(tmp.glob("resultado_completo*.txt"))
        report_text = reports[0].read_text(encoding="utf-8", errors="replace") if reports else ""
        objective_match = re.search(r"Valor da Função Objetivo:\s*([-+0-9.eE]+)", report_text)
        status_match = re.search(r"Status:\s*([^\r\n]+)", report_text)
        objective = float(objective_match.group(1)) if objective_match else None
        status = status_match.group(1).strip() if status_match else ("OK" if completed.returncode == 0 else "Error")
        error = completed.stderr.strip() if completed.returncode else ""
        return objective, status, error


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa as formulações clássicas Nash/GMR/SMR/SEQ/SSEQ.")
    parser.add_argument("--instance", default="5", help="5/nuclear ou 12/cuban")
    parser.add_argument("--criteria", default="all")
    parser.add_argument("--states", default="all")
    parser.add_argument("--solver", choices=["auto", "cbc", "cplex"], default="auto")
    parser.add_argument("--timeout", type=int, default=600, help="segundos por execução")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "classical")
    args = parser.parse_args()

    instance = get_instance(args.instance)
    states = parse_states(args.states, instance.states)
    criteria = list(SOURCES) if args.criteria.lower() == "all" else [x.strip().lower() for x in args.criteria.split(",")]
    unknown = [x for x in criteria if x not in SOURCES]
    if unknown:
        parser.error(f"Critérios desconhecidos: {', '.join(unknown)}")

    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = 0
    for criterion in criteria:
        row = [criterion.upper()]
        values = {state: None for state in range(instance.states)}
        for state in states:
            try:
                objective, status, error = run_one(criterion, instance, state, args.solver, args.timeout)
            except subprocess.TimeoutExpired:
                objective, status, error = None, "Timeout", ""
            values[state] = objective
            print(f"{criterion.upper():4s} estado={state+1:2d} status={status} custo={objective}")
            if objective is None:
                failures += 1
                if error:
                    print(error, file=sys.stderr)
        row.extend(values[state] for state in range(instance.states))
        rows.append(row)

    path = args.output / f"classical_{instance.key}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["criterion", *[f"state_{i}" for i in range(1, instance.states + 1)]])
        writer.writerows(rows)
    print(f"Resultados salvos em {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
