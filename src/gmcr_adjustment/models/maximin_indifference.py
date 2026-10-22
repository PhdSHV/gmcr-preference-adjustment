from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, CPLEX_CMD
from gmcr_adjustment.solver import solve_model

def ler_csv_inteiros(arquivo):
    matriz = []
    dados = open(arquivo, "r", encoding="utf-8").readlines()
    for linha in dados:
        matriz.append([int(x) for x in linha.split(",")])
    return matriz


def custo_maxmin_indiferenca(
        H,
        S,
        N,
        s,
        arquivo_J1,
        arquivo_J2,
        arquivo_P1,
        arquivo_P2
        ,
        solver="auto",
        msg=False
    ):

    horizonte_h = H
    S = range(S)
    N = range(N)

    J1 = ler_csv_inteiros(arquivo_J1)
    J2 = ler_csv_inteiros(arquivo_J2)
    J = [J1, J2]

    P1 = ler_csv_inteiros(arquivo_P1)
    P2 = ler_csv_inteiros(arquivo_P2)
    P = [P1, P2]

    M = len(S)
    Wmax = len(S) - 1

    model = LpProblem("Maxmin_com_Indiferenca", LpMinimize)

    D = [[[[LpVariable(f"D_{i}_{j}_{a}_{h}", 0, 1, cat="Binary")
            for h in range(0, horizonte_h + 1)]
           for a in S] for j in N] for i in N]

    Da = [[[[[LpVariable(f"Da_{i}_{j}_{a}_{b}_{h}", 0, 1, cat="Binary")
              for h in range(0, horizonte_h + 1)]
             for b in S] for a in S] for j in N] for i in N]

    W = [[LpVariable(f"W_{i}_{a}", lowBound=0, upBound=Wmax, cat="Integer")
          for a in S] for i in N]

    A = [[[[LpVariable(f"A_{i}_{j}_{a}_{h}", cat="Integer")
            for h in range(0, horizonte_h + 1)]
           for a in S] for j in N] for i in N]

    X1 = [[[LpVariable(f"X1_{i}_{a}_{b}", 0, 1, cat="Binary")
            for b in S] for a in S] for i in N]

    T = [[[LpVariable(f"T_{i}_{a}_{b}", 0, 1, cat="Binary")
           for b in S] for a in S] for i in N]

    K = [[sum(P[i][a][s0] for a in S) for s0 in S] for i in N]

    # Função objetivo
    model += lpSum(
        (
            T[i][a][b] + 2 * X1[i][a][b]
            if K[i][a] > K[i][b]
            else T[i][a][b] + 2 * X1[i][b][a]
            if K[i][a] < K[i][b]
            else X1[i][a][b] + X1[i][b][a]
        )
        for i in N for a in S for b in S if a < b
    )

    # R1 e R2
    for i in N:
        for a in S:
            for b in S:
                if a != b:
                    model += W[i][b] - W[i][a] >= 1 - M * (1 - X1[i][a][b])
                    model += W[i][b] - W[i][a] <= M * X1[i][a][b]

    # R3, R4 e R5
    for i in N:
        for a in S:
            for b in S:
                if a < b:
                    model += W[i][a] - W[i][b] <= M * (1 - T[i][a][b])
                    model += W[i][b] - W[i][a] <= M * (1 - T[i][a][b])
                    model += X1[i][a][b] + X1[i][b][a] + T[i][a][b] == 1

                elif a == b:
                    model += X1[i][a][b] == 0
                    model += T[i][a][b] == 1

    # R6 a R9
    for i in N:
        j = 1 - i

        for a in S:
            for h in range(1, horizonte_h + 1):
                model += A[i][i][a][h] >= W[i][a]
                model += A[i][i][a][h] <= W[i][a] + M * (1 - D[i][i][a][h])

                model += A[i][j][a][h] <= W[i][a]
                model += A[i][j][a][h] >= W[i][a] - M * (1 - D[i][j][a][h])

    # R10 a R13
    for i in N:
        j = 1 - i

        for a in S:
            for b in S:
                for h in range(1, horizonte_h + 1):

                    if J[i][a][b] == 1:
                        model += A[i][i][a][h] >= A[i][j][b][h - 1]
                        model += A[i][i][a][h] <= A[i][j][b][h - 1] + M * (1 - Da[i][i][a][b][h])

                    if J[j][a][b] == 1:
                        model += A[i][j][a][h] <= A[i][i][b][h - 1]
                        model += A[i][j][a][h] >= A[i][i][b][h - 1] - M * (1 - Da[i][j][a][b][h])

    # R14 e R15
    for i in N:
        j = 1 - i

        for a in S:
            for h in range(1, horizonte_h + 1):

                model += D[i][i][a][h] + lpSum(
                    Da[i][i][a][b][h]
                    for b in S if J[i][a][b] == 1
                ) == 1

                model += D[i][j][a][h] + lpSum(
                    Da[i][j][a][b][h]
                    for b in S if J[j][a][b] == 1
                ) == 1

    # R16, R17 e R18
    for i in N:
        j = 1 - i

        model += A[i][i][s][horizonte_h] == W[i][s]

        for a in S:
            model += A[i][i][a][0] == W[i][a]
            model += A[i][j][a][0] == W[i][a]

    solve_model(model, solver=solver, msg=msg)

    status = LpStatus[model.status]

    if status != "Optimal":
        return None, status, None

    W_values = {}

    for v in model.variables():
        if v.name.startswith("W_") and v.varValue is not None:

            partes = v.name.split("_")
            i = int(partes[1])
            a = int(partes[2])

            valor = int(round(v.varValue))

            if i not in W_values:
                W_values[i] = {}

            W_values[i][a] = valor

    return value(model.objective), status, W_values


