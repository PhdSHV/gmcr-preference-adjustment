#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    command = [sys.executable, *args]
    print("\n$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa toda a reprodução descrita no README.")
    parser.add_argument("--solver", choices=["auto", "cbc", "cplex"], default="cbc")
    parser.add_argument("--skip-classical", action="store_true")
    parser.add_argument("--skip-cuban", action="store_true")
    parser.add_argument("--solver-log", action="store_true")
    args = parser.parse_args()

    solver_log = ["--solver-log"] if args.solver_log else []
    if not args.skip_classical:
        run("scripts/reproduce_classical.py", "--instance", "5", "--solver", args.solver)
        if not args.skip_cuban:
            run("scripts/reproduce_classical.py", "--instance", "12", "--solver", args.solver)

    run("scripts/reproduce_lh.py", "--instance", "5", "--max-horizon", "15", "--solver", args.solver, *solver_log)
    run("scripts/reproduce_maximin.py", "--instance", "5", "--max-horizon", "15", "--solver", args.solver, *solver_log)
    if not args.skip_cuban:
        run("scripts/reproduce_lh.py", "--instance", "12", "--max-horizon", "6", "--solver", args.solver, *solver_log)
        run("scripts/reproduce_maximin.py", "--instance", "12", "--max-horizon", "6", "--solver", args.solver, *solver_log)

    run("scripts/verify_results.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
