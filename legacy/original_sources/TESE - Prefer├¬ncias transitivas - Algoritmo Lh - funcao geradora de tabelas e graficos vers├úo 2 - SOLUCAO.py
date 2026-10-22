from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD, CPLEX_CMD
import matplotlib.pyplot as plt
import csv
import math
import os
import time

# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================

# Defina aqui o horizonte máximo H para cada conflito
H_por_conflito = {
    5: 15,
    12: 6
    #36: 2
}

# Se quiser usar CPLEX, deixe True. Caso contrário, coloque False para usar CBC.
usar_cplex = True

# Pasta de saída
pasta_saida = "resultados_Lh_todos_estados"
os.makedirs(pasta_saida, exist_ok=True)


# ==========================================================
# LEITURA DAS MATRIZES (MANTENDO O PADRÃO ORIGINAL)
# ==========================================================

def ler_matriz_csv(nome_arquivo):
    matriz = []

    dados = open(nome_arquivo, 'r').readlines()

    for x in dados:
        texto = x.split(',')

        linha_int = []

        for k in texto:
            linha_int.append(int(k))

        matriz.append(linha_int)

    return matriz


def carregar_conflito(num_estados):
    # Conjuntos
    S = set(range(num_estados))
    N = set(range(2))  # modelo original bilateral

    # Ler J1
    J1 = ler_matriz_csv(f'J1-{num_estados}est.csv')

    # Ler J2
    J2 = ler_matriz_csv(f'J2-{num_estados}est.csv')
    J = [J1, J2]

    # Ler P1
    P1 = ler_matriz_csv(f'P1-{num_estados}est.csv')

    # Ler P2
    P2 = ler_matriz_csv(f'P2-{num_estados}est.csv')
    P = [P1, P2]

    return S, N, J, P


# ==========================================================
# SOLVER DO MODELO Lh PARA UM ESTADO s E UM HORIZONTE h
# ==========================================================

def resolver_Lh(num_estados, s_focal, horizonte_h):
    S, N, J, P = carregar_conflito(num_estados)

    # Modelo
    model = LpProblem("Optimization_Model", LpMinimize)

    # Variáveis de decisão
    C = [[[LpVariable(f"C_{i}_{a}_{b}", 0, 1, cat="Binary") for b in S] for a in S] for i in N]
    D = [[[LpVariable(f"D_{i}_{a}_{h}", 0, 1, cat="Binary") for h in range(0, horizonte_h + 1)] for a in S] for i in N]
    Da = [[[[LpVariable(f"Da_{i}_{a}_{b}_{h}", 0, 1, cat="Binary") for h in range(0, horizonte_h + 1)] for b in S] for a in S] for i in N]
    W = [[LpVariable(f"W_{i}_{a}", cat="Integer") for a in S] for i in N]
    t = [[[LpVariable(f"t_{i}_{a}_{b}", 0, 1, cat="Binary") for b in S] for a in S] for i in N]
    B = [[[[LpVariable(f"B_{i}_{a}_{b}_{h}", cat="Integer") for h in range(0, horizonte_h + 1)] for b in S] for a in S] for i in N]
    V = [[[LpVariable(f"V_{i}_{a}_{h}", cat="Integer") for h in range(0, horizonte_h + 1)] for a in S] for i in N]
    Z1 = [[[LpVariable(f"Z1_{i}_{a}_{h}", cat="Integer") for h in range(0, horizonte_h + 1)] for a in S] for i in N]
    Z2 = [[[[LpVariable(f"Z2_{i}_{a}_{b}_{h}", cat="Integer") for h in range(0, horizonte_h + 1)] for b in S] for a in S] for i in N]

    # Calcular K
    K = [[sum(P[i][a][s] for a in S) for s in S] for i in N]

    M = len(S)

    # Função objetivo
    objective = lpSum(C[i][a][b] for i in N for a in S for b in S if a != b)
    model += objective

    # ==================== Restrição 1 =======================
    for i in N:
        for a in S:
            for b in S:
                if a != b:
                    model += C[i][a][b] * (len(S) - 1) * (len(S) - 1) >= (W[i][a] - W[i][b]) * (K[i][b] - K[i][a])

    # ==================== Restrição 2 =======================
    for i in N:
        for a in S:
            for h in range(1, horizonte_h + 1):
                model += D[i][a][h] + lpSum(Da[i][a][b][h] for b in S if J[i][a][b] == 1) == 1

    # ==================== Restrições de linearização de W =======================
    for i in N:
        for a in S:
            model += lpSum(t[i][a][b] for b in range(len(S))) == 1

    for i in N:
        for a in S:
            model += lpSum(b * t[i][a][b] for b in range(len(S))) == W[i][a]

    for i in N:
        for b in range(len(S)):
            model += lpSum(t[i][a][b] for a in S) == 1

    # ==================== Inicialização de B e V =======================
    for i in N:
        for a in S:
            model += V[i][a][0] == W[i][a]
            for h in range(1, horizonte_h + 1):
                model += B[i][a][a][h] == W[i][a]
            for b in S:
                if J[i][a][b] == 1:
                    model += B[i][a][b][1] == W[i][b]

    # ==================== Recursão e linearização =======================
    for i in N:
        for a in S:
            for b in S:
                if J[i][a][b] == 1:
                    for h in range(1, horizonte_h + 1):
                        model += V[i][a][h] >= B[i][a][b][h]
                        model += V[i][a][h] <= B[i][a][b][h] + (len(S) - 1) * (1 - Da[i][a][b][h])
                        model += V[i][a][h] >= W[i][a]
                        model += V[i][a][h] <= W[i][a] + (len(S) - 1) * (1 - D[i][a][h])

                        if horizonte_h >= 2 and h >= 2:
                            model += B[i][a][b][h] == Z1[i][b][h - 1] + lpSum(Z2[i][b][c][h - 1] for c in S if J[1 - i][b][c] == 1)

                            # Z1 = D[1-i][b][h-1] * W[i][b]
                            model += Z1[i][b][h - 1] <= W[i][b]
                            model += Z1[i][b][h - 1] <= M * D[1 - i][b][h - 1]
                            model += Z1[i][b][h - 1] >= W[i][b] - M * (1 - D[1 - i][b][h - 1])
                            model += Z1[i][b][h - 1] >= 0

                            # Z2 = Da[1-i][b][c][h-1] * V[i][c][h-2]
                            for c in S:
                                if J[1 - i][b][c] == 1:
                                    model += Z2[i][b][c][h - 1] <= V[i][c][h - 2]
                                    model += Z2[i][b][c][h - 1] <= M * Da[1 - i][b][c][h - 1]
                                    model += Z2[i][b][c][h - 1] >= V[i][c][h - 2] - M * (1 - Da[1 - i][b][c][h - 1])
                                    model += Z2[i][b][c][h - 1] >= 0

    # ==================== Restrição condicional =======================
    for i in N:
        for a in S:
            for h in range(1, horizonte_h + 1):
                model += V[i][a][h] - W[i][a] >= 1 - D[i][a][h]

        # Condição de equilíbrio
        model += V[i][s_focal][horizonte_h] == W[i][s_focal]

    # ==================== Resolver =======================
    try:
        if usar_cplex:
            model.solve(CPLEX_CMD(msg=False))
        else:
            model.solve(PULP_CBC_CMD(msg=False))
    except:
        model.solve()

    status = LpStatus[model.status]

    if status != "Optimal":
        return None, status, None, K

    W_values = {}

    for v in model.variables():
        if v.name.startswith("W_") and v.varValue is not None:
            parts = v.name.split("_")
            i = int(parts[1])
            a = int(parts[2])
            valor = int(round(v.varValue))

            if i not in W_values:
                W_values[i] = {}
            W_values[i][a] = valor

    return model.objective.value(), status, W_values, K


# ==========================================================
# SALVAR CSV
# ==========================================================

def salvar_tabela_csv(num_estados, horizontes, tabela_custos):
    nome_csv = os.path.join(pasta_saida, f"custos_Lh_{num_estados}est_ate_{horizontes[-1]}_horizontes.csv")

    with open(nome_csv, mode="w", newline="") as arquivo:
        escritor = csv.writer(arquivo)

        cabecalho = ["estado"] + [f"h={h}" for h in horizontes]
        escritor.writerow(cabecalho)

        for estado, custos in tabela_custos.items():
            linha = [estado + 1] + custos
            escritor.writerow(linha)
        

    return nome_csv


# ==========================================================
# GERAR GRÁFICO
# ==========================================================

def gerar_grafico(num_estados, horizontes, tabela_custos):
    plt.figure(figsize=(10, 6))

    for estado, custos in tabela_custos.items():
        plt.plot(horizontes, custos, marker='o', label=f"Estado {estado + 1}")
    
    plt.xlabel("Horizonte")
    plt.ylabel("Custo")
    plt.title(f"Custos ótimos do modelo Lh - conflito com {num_estados} estados")
    plt.xticks(horizontes)
    plt.grid(True)
    plt.legend(loc="best", fontsize=8)

    nome_png = os.path.join(pasta_saida, f"grafico_Lh_{num_estados}est_ate_{horizontes[-1]}_horizontes.png")
    plt.tight_layout()
    plt.savefig(nome_png, dpi=300)
    plt.close()

    return nome_png


# ==========================================================
# RODAR UM CONFLITO
# ==========================================================

def rodar_conflito(num_estados, H_max):
    S = set(range(num_estados))
    horizontes = list(range(1, H_max + 1))

    tabela_custos = {}
    tabela_preferencias = {}
    print(f"\nRodando conflito com {num_estados} estados...")
    inicio = time.time()

    for estado_focal in S:
        custos_estado = []
        print(f"  Estado focal s = {estado_focal + 1}")

        for h in horizontes:
            custo, status, W_values, K = resolver_Lh(num_estados, estado_focal, h)

            if custo is None:
                print(f"    horizonte {h}: status = {status}")
                custos_estado.append("")
            else:
                print(f"    horizonte {h}: custo = {custo}")
                custos_estado.append(custo)
                
            if estado_focal not in tabela_preferencias:
                tabela_preferencias[estado_focal] = {}

            tabela_preferencias[estado_focal][h] = W_values

        tabela_custos[estado_focal] = custos_estado
       
    nome_csv = salvar_tabela_csv(num_estados, horizontes, tabela_custos)
    nome_png = gerar_grafico(num_estados, horizontes, tabela_custos)
    fim = time.time()
    tempo_total = fim - inicio
    with open(os.path.join(pasta_saida, f"relatorio_{num_estados}est_ate_{horizontes[-1]}_horizontes.txt"), "w") as f:
        f.write(f"============ Conflito {num_estados} estados ==================\n\n")

        f.write("==================================================\n")
        f.write("========== Preferência original (P_i): ===========\n\n")

        for i in range(len(K)):
            estados_K = [(s_idx, K[i][s_idx]) for s_idx in range(len(K[i]))]
            estados_K.sort(key=lambda x: x[1], reverse=True)

            # +1 por causa do zero offset
            preferencia = [str(s_idx + 1) for s_idx, _ in estados_K]
            relacao_preferencia = " > ".join(preferencia)

            f.write(f"P_{i+1}: {relacao_preferencia}\n")

        f.write("\n======= NOVAS PREFERÊNCIAS GERADAS (P'_i): =======\n")

        for estado_focal in sorted(tabela_preferencias.keys()):
            f.write(f"\n================= s = {estado_focal + 1} ==========================\n")

            for h in sorted(tabela_preferencias[estado_focal].keys()):
                f.write(f"\n\th={h}:\n\n")
                f.write(f"Custo: {tabela_custos[estado_focal][h-1]}\n\n")

                W_values = tabela_preferencias[estado_focal][h]

                if W_values is None:
                    f.write("Modelo sem solução ótima.\n")
                else:
                    for i in sorted(W_values.keys()):
                        sorted_states = sorted(W_values[i].items(), key=lambda x: x[1], reverse=True)

                        # +1 por causa do zero offset
                        preferencia = " > ".join(str(a + 1) for a, _ in sorted_states)
                        f.write(f"P'_{i+1}: {preferencia}\n")

        f.write(f"\nTempo total de execução: {tempo_total:.2f} segundos\n")
        f.write(f"Tempo total de execução: {tempo_total/60:.2f} minutos\n")


# ==========================================================
# RODAR OS 3 CONFLITOS
# ==========================================================

for num_estados in H_por_conflito:
    rodar_conflito(num_estados, H_por_conflito[num_estados])

print("\nProcesso finalizado.")