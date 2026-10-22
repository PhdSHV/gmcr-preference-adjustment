# Algoritmo Maximin sem indiferença - Multi decisores
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value, PULP_CBC_CMD, CPLEX_CMD
import math
import numpy

# ==========================================================
# Conjuntos
# ==========================================================
horizonte_h = 2          # Horizonte de movimento limitado
S = set(range(5))        # Conjunto de estados
N = set(range(2))        # Conjunto de decisores (ex.: 3 decisores)
s = 1                    # Estado focal


# ==========================================================
# LEITURA DAS MATRIZES - MANTENDO O PADRÃO ORIGINAL
# ==========================================================

# ---------- Ler os arquivos J ----------
J = []

for decisor in range(1, len(N) + 1):

    Ji = []   # cria uma lista vazia

    dados = open(f'J{decisor}-5est.csv', 'r').readlines()  # puxa dados de arquivo externo

    for x in dados:
        Jtexto = x.split(',')

        Jint = []   # cria uma lista vazia

        for k in Jtexto:
            Jint.append(int(k))

        Ji.append(Jint)

    J.append(Ji)


# ---------- Ler os arquivos P ----------
P = []

for decisor in range(1, len(N) + 1):

    Pi = []   # cria uma lista vazia

    dados = open(f'P{decisor}-5est.csv', 'r').readlines()  # puxa dados de arquivo externo

    for x in dados:
        Ptexto = x.split(',')

        Pint = []   # cria uma lista vazia

        for k in Ptexto:
            Pint.append(int(k))

        Pi.append(Pint)

    P.append(Pi)


# ==========================================================
# CONSTRUÇÃO DE J_opp
# J_opp[i][a][b] = 1 se b puder ser alcançado a partir de a
# pelos oponentes de i, com movimentos unilaterais,
# sem que o mesmo oponente se mova duas vezes seguidas.
# ==========================================================

J_opp = [[[0 for b in S] for a in S] for i in N]


def reachable_by_opponents_alternating(a_inicial, i_focal):
    """
    Retorna o conjunto de estados alcançáveis a partir de a_inicial
    pelos oponentes de i_focal, com alternância de movedor:
    um mesmo oponente não pode mover duas vezes consecutivas.
    """
    stack = [(a_inicial, None)]   # (estado atual, último oponente que moveu)
    visited = set()
    reachable = set()

    while stack:
        current_state, last_mover = stack.pop()

        for j in N:
            if j == i_focal:
                continue

            if j == last_mover:
                continue

            for b in S:
                if J[j][current_state][b] == 1 and b != current_state:
                    key = (b, j)
                    if key not in visited:
                        visited.add(key)
                        reachable.add(b)
                        stack.append((b, j))

    return reachable


for i in N:
    for a in S:
        R_opp = reachable_by_opponents_alternating(a, i)
        for b in R_opp:
            J_opp[i][a][b] = 1


# ==========================================================
# MODELO
# ==========================================================
model = LpProblem("Optimization_Model", LpMinimize)

# Variáveis de decisão
C = [[[LpVariable(f"C_{i}_{a}_{b}", 0, 1, cat="Binary") for b in S] for a in S] for i in N]

# Mantendo separadas as partes do decisor focal e dos oponentes
D_self = [[[LpVariable(f"Dself_{i}_{a}_{h}", 0, 1, cat="Binary")
            for h in range(0, horizonte_h + 1)] for a in S] for i in N]

D_opp = [[[LpVariable(f"Dopp_{i}_{a}_{h}", 0, 1, cat="Binary")
           for h in range(0, horizonte_h + 1)] for a in S] for i in N]

Da_self = [[[[LpVariable(f"Daself_{i}_{a}_{b}_{h}", 0, 1, cat="Binary")
              for h in range(0, horizonte_h + 1)] for b in S] for a in S] for i in N]

Da_opp = [[[[LpVariable(f"Daopp_{i}_{a}_{b}_{h}", 0, 1, cat="Binary")
             for h in range(0, horizonte_h + 1)] for b in S] for a in S] for i in N]

W = [[LpVariable(f"W_{i}_{a}", cat="Integer") for a in S] for i in N]

A_self = [[[LpVariable(f"Aself_{i}_{a}_{h}", cat="Integer")
            for h in range(0, horizonte_h + 1)] for a in S] for i in N]

A_opp = [[[LpVariable(f"Aopp_{i}_{a}_{h}", cat="Integer")
           for h in range(0, horizonte_h + 1)] for a in S] for i in N]

t = [[[LpVariable(f"t_{i}_{a}_{b}", 0, 1, cat="Binary") for b in S] for a in S] for i in N]


# ==========================================================
# Calcular K para todos os estados e decisores
# ==========================================================
K = [[sum(P[i][a][s0] for a in S) for s0 in S] for i in N]


# ==========================================================
# Função objetivo
# ==========================================================
objective = lpSum(C[i][a][b] for i in N for a in S for b in S if a != b)
model += objective


# ==========================================================
# Restrição 1
# ==========================================================
for i in N:
    for a in S:
        for b in S:
            if a != b:
                for c in S:
                    model += C[i][a][b] * (len(S) - 1) * (len(S) - 1) >= (W[i][a] - W[i][b]) * (K[i][b] - K[i][a])


# ==========================================================
# Restrições 2, 3, 4 e 5
# ==========================================================
for i in N:
    for a in S:
        for h in range(1, horizonte_h + 1):
            model += A_self[i][a][h] >= W[i][a]
            model += A_self[i][a][h] <= W[i][a] + (len(S) - 1) * (1 - D_self[i][a][h])

            model += A_opp[i][a][h] <= W[i][a]
            model += A_opp[i][a][h] >= W[i][a] - (len(S) - 1) * (1 - D_opp[i][a][h])


# ==========================================================
# Restrições 6, 7, 8 e 9
# ==========================================================
for i in N:
    for a in S:
        for b in S:
            for h in range(1, horizonte_h + 1):

                # Movimento do próprio decisor i
                if J[i][a][b] == 1:
                    model += A_self[i][a][h] >= A_opp[i][b][h - 1]
                    model += A_self[i][a][h] <= A_opp[i][b][h - 1] + (len(S) - 1) * (1 - Da_self[i][a][b][h])

                # Movimento agregado dos oponentes
                if J_opp[i][a][b] == 1:
                    model += A_opp[i][a][h] <= A_self[i][b][h - 1]
                    model += A_opp[i][a][h] >= A_self[i][b][h - 1] - (len(S) - 1) * (1 - Da_opp[i][a][b][h])


# ==========================================================
# Restrição 10 - separada em duas para múltiplos decisores
# ==========================================================
for i in N:
    for a in S:
        for h in range(1, horizonte_h + 1):
            model += D_self[i][a][h] + lpSum(Da_self[i][a][b][h] for b in S if J[i][a][b] == 1) == 1

for i in N:
    for a in S:
        for h in range(1, horizonte_h + 1):
            model += D_opp[i][a][h] + lpSum(Da_opp[i][a][b][h] for b in S if J_opp[i][a][b] == 1) == 1


# ==========================================================
# Restrições 11, 12 e 13
# ==========================================================
for i in N:
    model += A_self[i][s][horizonte_h] == W[i][s]

for i in N:
    for a in S:
        model += A_self[i][a][0] == W[i][a]
        model += A_opp[i][a][0] == W[i][a]


# ==========================================================
# Restrições 14, 15 e 16
# ==========================================================
for i in N:
    for a in S:
        model += lpSum(t[i][a][b] for b in range(len(S))) == 1

for i in N:
    for a in S:
        model += lpSum(b * t[i][a][b] for b in range(len(S))) == W[i][a]

for i in N:
    for b in range(len(S)):
        model += lpSum(t[i][a][b] for a in S) <= 1


# ==========================================================
# Resolução
# ==========================================================
# model.solve(CPLEX_CMD(msg=True))
model.solve(PULP_CBC_CMD(msg=True))


# ==========================================================
# Relatório final
# ==========================================================
with open("resultado_completo_MaxMin_MultiDM.txt", "w") as f:
    f.write("Relatório de Resultados - Modelo de Programação Linear MultiDM\n")
    f.write("=" * 60 + "\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write("VALORES DAS VARIÁVEIS W (TODOS):\n")

    W_values = {}

    for v in model.variables():
        if v.name.startswith("W_") and v.varValue is not None:
            parts = v.name.split("_")
            i = int(parts[1])
            a = int(parts[2])
            valor = int(round(v.varValue))
            f.write(f"{v.name} = {valor}\n")

            if i not in W_values:
                W_values[i] = {}
            W_values[i][a] = valor

    for i in range(len(K)):
        f.write(f"\nVALORES DE K_{i} (TODOS):\n")
        for s_idx, valor in enumerate(K[i]):
            f.write(f"K_{i}_{s_idx} = {valor}\n")

    f.write("\n" + "=" * 50 + "\n")
    f.write(f"Preferência original (P_i): \n")

    for i in range(len(K)):
        estados_K = [(s_idx, K[i][s_idx]) for s_idx in range(len(K[i]))]
        estados_K.sort(key=lambda x: x[1], reverse=True)
        preferencia = [str(s_idx) for s_idx, _ in estados_K]
        relacao_preferencia = " > ".join(preferencia)
        f.write(f"P_{i}: {relacao_preferencia}\n")

    f.write("\n" + "=" * 50 + "\n")
    f.write("NOVAS PREFERÊNCIAS GERADAS (P'_i):\n")

    for i in sorted(W_values.keys()):
        sorted_states = sorted(W_values[i].items(), key=lambda x: x[1], reverse=True)
        preferencia = " > ".join(str(a) for a, _ in sorted_states)
        f.write(f"P'_{i}: {preferencia}\n")

    f.write(f"\nValor da Função Objetivo: {model.objective.value()}\n")

    f.write("Formulação do Modelo:\n")
    f.write("Função Objetivo: " + str(model.objective) + "\n")

    f.write("\nRestrições:\n")
    for name, constraint in model.constraints.items():
        f.write(f"{name}: {constraint}\n")

    f.write("\nResultados:\n")
    f.write(f"Status: {LpStatus[model.status]}\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write("VARIÁVEIS C_ COM VALOR DIFERENTE DE ZERO:\n")
    f.write("=" * 60 + "\n")

    for v in model.variables():
        if v.name.startswith("C_") and v.varValue not in (0, None):
            valor = int(v.varValue) if v.varValue in (0.0, 1.0) else v.varValue
            f.write(f"{v.name} = {valor}\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write("VARIÁVEIS SEM VALOR ATRIBUÍDO (None):\n")
    f.write("=" * 60 + "\n")

    for v in model.variables():
        if v.varValue is None:
            f.write(f"{v.name} = None\n")

    f.write("\n" + "=" * 60 + "\n")
    f.write("MATRIZ J_opp (ACESSIBILIDADE DOS OPONENTES COM ALTERNÂNCIA):\n")
    f.write("=" * 60 + "\n")

    for i in N:
        f.write(f"\nJ_opp para o decisor focal i = {i}\n")
        estados = list(S)
        f.write("      " + " ".join(f"b={b:2}" for b in estados) + "\n")
        f.write("-" * (8 + len(estados) * 5) + "\n")

        for a in estados:
            linha = f"a={a:2} | " + " ".join(f"{J_opp[i][a][b]:2d}" for b in estados)
            f.write(linha + "\n")

    f.write("=" * 50 + "\n")
    f.write("Relatório Finalizado.")