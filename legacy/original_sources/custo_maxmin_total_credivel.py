from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, CPLEX_CMD

def ler_csv_inteiros(arquivo):
    matriz = []
    dados = open(arquivo, "r").readlines()
    for linha in dados:
        matriz.append([int(x) for x in linha.split(",")])
    return matriz


def custo_maxmin_total_credivel(
        H,
        S,
        N,
        s,
        arquivo_J1,
        arquivo_J2,
        arquivo_P1,
        arquivo_P2
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

    model = LpProblem("Maximin_Total_Credivel", LpMinimize)

    C = [[[LpVariable(f"C_{i}_{a}_{b}", 0, 1, cat="Binary")
           for b in S] for a in S] for i in N]

    D = [[[[LpVariable(f"D_{i}_{j}_{a}_{h}", 0, 1, cat="Binary")
            for h in range(0, horizonte_h + 1)]
           for a in S] for j in N] for i in N]

    Da = [[[[[LpVariable(f"Da_{i}_{j}_{a}_{b}_{h}", 0, 1, cat="Binary")
              for h in range(0, horizonte_h + 1)]
             for b in S] for a in S] for j in N] for i in N]

    W = [[LpVariable(f"W_{i}_{a}", lowBound=0, upBound=M, cat="Integer")
          for a in S] for i in N]

    A = [[[[LpVariable(f"A_{i}_{j}_{a}_{h}", cat="Integer")
            for h in range(0, horizonte_h + 1)]
           for a in S] for j in N] for i in N]

    t = [[[LpVariable(f"t_{i}_{a}_{b}", 0, 1, cat="Binary")
           for b in S] for a in S] for i in N]

    X1 = [[[LpVariable(f"X1_{i}_{a}_{b}", 0, 1, cat="Binary")
            for b in S] for a in S] for i in N]

    Z3 = [[[[[LpVariable(f"Z3_{i}_{j}_{a}_{b}_{h}", 0, 1, cat="Binary")
              for h in range(0, horizonte_h + 1)]
             for b in S] for a in S] for j in N] for i in N]

    K = [[sum(P[i][a][s0] for a in S) for s0 in S] for i in N]

    # Função objetivo
    model += lpSum(C[i][a][b] for i in N for a in S for b in S if a != b)

    # R1
    for i in N:
        for a in S:
            for b in S:
                if a != b:
                    model += C[i][a][b] * M * M >= (W[i][a] - W[i][b]) * (K[i][b] - K[i][a])

    # R2 e R3
    for i in N:
        for a in S:
            for b in S:
                if a != b:
                    model += W[i][b] >= W[i][a] + 1 - M * (1 - X1[i][a][b])
                    model += W[i][b] <= W[i][a] + M * X1[i][a][b]

    # X1_ab + X1_ba = 1, para todo decisor
    for i in N:
        for a in S:
            for b in S:
                if a < b:
                    model += X1[i][a][b] + X1[i][b][a] == 1
                elif a == b:
                    model += X1[i][a][b] == 0

    # R4 a R7
    for i in N:
        j = 1 - i
        for a in S:
            for h in range(1, horizonte_h + 1):
                model += A[i][i][a][h] >= W[i][a]
                model += A[i][i][a][h] <= W[i][a] + M * (1 - D[i][i][a][h])

                model += A[i][j][a][h] <= W[i][a]
                model += A[i][j][a][h] >= W[i][a] - M * (1 - D[i][j][a][h])

    # R8 e R9: focal credível
    for i in N:
        j = 1 - i
        for a in S:
            for b in S:
                for h in range(1, horizonte_h + 1):
                    if J[i][a][b] == 1:
                        model += A[i][i][a][h] >= A[i][j][b][h - 1] - M * (1 - X1[i][a][b])
                        model += A[i][i][a][h] <= A[i][j][b][h - 1] + M * (2 - Da[i][i][a][b][h] - X1[i][a][b])

    # R10 e R11: oponente credível
    for i in N:
        j = 1 - i
        for a in S:
            for b in S:
                for h in range(1, horizonte_h + 1):
                    if J[j][a][b] == 1:
                        model += A[i][j][a][h] <= A[i][i][b][h - 1] + M * (1 - X1[j][a][b])
                        model += A[i][j][a][h] >= A[i][i][b][h - 1] - M * (2 - Da[i][j][a][b][h] - X1[j][a][b])

    # R12: escolha focal com Z3^{i,i}
    for i in N:
        for a in S:
            for h in range(1, horizonte_h + 1):
                model += D[i][i][a][h] + lpSum(
                    Z3[i][i][a][b][h]
                    for b in S if J[i][a][b] == 1
                ) == 1

    # R13: escolha do oponente com Z3^{i,j}
    for i in N:
        j = 1 - i
        for a in S:
            for h in range(1, horizonte_h + 1):
                model += D[i][j][a][h] + lpSum(
                    Z3[i][j][a][b][h]
                    for b in S if J[j][a][b] == 1
                ) == 1

    # R14, R15, R16: Z3^{i,i} = Da^{i,i} * X1^i
    for i in N:
        for a in S:
            for b in S:
                for h in range(1, horizonte_h + 1):
                    if J[i][a][b] == 1:
                        model += Z3[i][i][a][b][h] <= Da[i][i][a][b][h]
                        model += Z3[i][i][a][b][h] <= X1[i][a][b]
                        model += Z3[i][i][a][b][h] >= Da[i][i][a][b][h] + X1[i][a][b] - 1

    # R17, R18, R19: Z3^{i,j} = Da^{i,j} * X1^j
    for i in N:
        j = 1 - i
        for a in S:
            for b in S:
                for h in range(1, horizonte_h + 1):
                    if J[j][a][b] == 1:
                        model += Z3[i][j][a][b][h] <= Da[i][j][a][b][h]
                        model += Z3[i][j][a][b][h] <= X1[j][a][b]
                        model += Z3[i][j][a][b][h] >= Da[i][j][a][b][h] + X1[j][a][b] - 1

    # R20, R21, R22
    for i in N:
        j = 1 - i

        model += A[i][i][s][horizonte_h] == W[i][s]

        for a in S:
            model += A[i][i][a][0] == W[i][a]
            model += A[i][j][a][0] == W[i][a]

    # R23, R24, R25
    for i in N:
        for a in S:
            model += lpSum(t[i][a][b] for b in S) == 1
            model += lpSum(b * t[i][a][b] for b in S) == W[i][a]

    for i in N:
        for b in S:
            model += lpSum(t[i][a][b] for a in S) <= 1
   
    model.solve(CPLEX_CMD(msg=False))

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

if __name__ == "__main__":

    fo, status, W = custo_maxmin_total_credivel(
        H=1,
        S=5,
        N=2,
        s=1,
        arquivo_J1="J1-5est.csv",
        arquivo_J2="J2-5est.csv",
        arquivo_P1="P1-5est.csv",
        arquivo_P2="P2-5est.csv"
    )

    print("Status =", status)
    print("FO =", fo)
    print("W =", W)