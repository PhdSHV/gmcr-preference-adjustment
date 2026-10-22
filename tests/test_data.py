from pathlib import Path


def read_matrix(path: Path):
    return [[int(x) for x in line.strip().split(",")] for line in path.read_text().splitlines() if line.strip()]


def test_matrix_dimensions():
    root = Path(__file__).resolve().parents[1]
    for dirname, n in [("nuclear_5_states", 5), ("cuban_missile_crisis_12_states", 12)]:
        for name in ("J1", "J2", "P1", "P2"):
            matrix = read_matrix(root / "data" / dirname / f"{name}.csv")
            assert len(matrix) == n
            assert all(len(row) == n for row in matrix)
            assert all(value in (0, 1) for row in matrix for value in row)
