from __future__ import annotations

from typing import Literal

from pulp import CPLEX_CMD, PULP_CBC_CMD

SolverName = Literal["auto", "cbc", "cplex"]


def get_solver(name: SolverName = "auto", msg: bool = False):
    """Return an available PuLP solver command.

    ``auto`` prefers CPLEX when it is installed and falls back to CBC.
    """
    normalized = name.lower()
    if normalized not in {"auto", "cbc", "cplex"}:
        raise ValueError(f"Solver desconhecido: {name}")

    cplex = CPLEX_CMD(msg=msg)
    cbc = PULP_CBC_CMD(msg=msg)

    if normalized == "cplex":
        if not cplex.available():
            raise RuntimeError("CPLEX não foi encontrado. Use --solver cbc ou instale/configure o CPLEX.")
        return cplex
    if normalized == "cbc":
        if not cbc.available():
            raise RuntimeError("CBC não foi encontrado pela instalação do PuLP.")
        return cbc

    if cplex.available():
        return cplex
    if cbc.available():
        return cbc
    raise RuntimeError("Nenhum solver disponível. Instale CBC (via PuLP) ou configure o CPLEX.")


def solve_model(model, solver: SolverName = "auto", msg: bool = False):
    return model.solve(get_solver(solver, msg=msg))
