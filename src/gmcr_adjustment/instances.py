from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Instance:
    key: str
    states: int
    directory: Path

    @property
    def files(self) -> dict[str, Path]:
        return {name: self.directory / f"{name}.csv" for name in ("J1", "J2", "P1", "P2")}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_instance(value: str | int) -> Instance:
    root = repository_root()
    aliases = {
        "5": ("nuclear_5_states", 5),
        "nuclear": ("nuclear_5_states", 5),
        "nuclear_5_states": ("nuclear_5_states", 5),
        "12": ("cuban_missile_crisis_12_states", 12),
        "cuba": ("cuban_missile_crisis_12_states", 12),
        "cuban": ("cuban_missile_crisis_12_states", 12),
        "cuban_missile_crisis_12_states": ("cuban_missile_crisis_12_states", 12),
    }
    key = str(value).lower()
    if key not in aliases:
        raise ValueError("Instância deve ser 5/nuclear ou 12/cuban.")
    dirname, states = aliases[key]
    directory = root / "data" / dirname
    return Instance(dirname, states, directory)
