import os
import csv
import time
import matplotlib.pyplot as plt
#from docx import Document

from custo_maxmin import custo_maxmin
from custo_maxmin_credivel import custo_maxmin_credivel
from custo_maxmin_indiferenca import custo_maxmin_indiferenca
from custo_maxmin_oponente_credivel import custo_maxmin_oponente_credivel
from custo_maxmin_total_credivel import custo_maxmin_total_credivel


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

H_por_conflito = {
    5: 6,
    12: 6
    # 36: 2
}

N_DECISORES = 2

PASTA_BASE = "Resultados Maxmin"
PASTA_RELATORIOS = os.path.join(PASTA_BASE, "Relatórios")
PASTA_GRAFICOS = os.path.join(PASTA_BASE, "Gráficos")
PASTA_TABELAS = os.path.join(PASTA_BASE, "Tabela")

os.makedirs(PASTA_RELATORIOS, exist_ok=True)
os.makedirs(PASTA_GRAFICOS, exist_ok=True)
os.makedirs(PASTA_TABELAS, exist_ok=True)


CRITERIOS = {
    "Maximin": custo_maxmin,
    "Maximin Credível": custo_maxmin_credivel,
    "Maximin com Indiferença": custo_maxmin_indiferenca,
    "Maximin Oponente Credível": custo_maxmin_oponente_credivel,
    "Maximin Total Credível": custo_maxmin_total_credivel
}


# ==========================================================
# LEITURA DAS MATRIZES
# ==========================================================

def ler_matriz_csv(nome_arquivo):
    matriz = []
    with open(nome_arquivo, "r") as arquivo:
        for linha in arquivo:
            matriz.append([int(x) for x in linha.strip().split(",")])
    return matriz


def carregar_preferencias_originais(num_estados):
    P = []

    for i in range(1, N_DECISORES + 1):
        P_i = ler_matriz_csv(f"P{i}-{num_estados}est.csv")
        P.append(P_i)

    S = range(num_estados)

    K = [
        [sum(P[i][a][s] for a in S) for s in S]
        for i in range(N_DECISORES)
    ]

    return K


def preferencias_a_partir_de_K(K):
    preferencias = {}

    for i in range(len(K)):
        estados_K = [(s_idx, K[i][s_idx]) for s_idx in range(len(K[i]))]
        estados_K.sort(key=lambda x: x[1], reverse=True)

        # +1 por causa do zero offset
        preferencias[i] = " > ".join(str(s_idx + 1) for s_idx, _ in estados_K)

    return preferencias


def preferencias_a_partir_de_W(W_values, permitir_empate=False):

    if W_values is None:
        return None

    preferencias = {}

    for i in sorted(W_values.keys()):

        estados_W = list(W_values[i].items())

        # ordena maior para menor valor de W
        estados_W.sort(key=lambda x: x[1], reverse=True)

        # -------------------------------------------------
        # CASO NORMAL: sem indiferença
        # -------------------------------------------------
        if not permitir_empate:

            preferencias[i] = " > ".join(
                str(a + 1) for a, _ in estados_W
            )

        # -------------------------------------------------
        # CASO COM INDIFERENÇA
        # -------------------------------------------------
        else:

            grupos = []
            grupo_atual = [str(estados_W[0][0] + 1)]
            valor_atual = estados_W[0][1]

            for a, valor in estados_W[1:]:

                if valor == valor_atual:
                    grupo_atual.append(str(a + 1))

                else:
                    grupos.append(grupo_atual)
                    grupo_atual = [str(a + 1)]
                    valor_atual = valor

            grupos.append(grupo_atual)

            partes = []

            for g in grupos:
                if len(g) == 1:
                    partes.append(g[0])
                else:
                    partes.append(" ~ ".join(g))

            preferencias[i] = " > ".join(partes)

    return preferencias


# ==========================================================
# NORMALIZAR RETORNO DAS FUNÇÕES
# ==========================================================

def normalizar_retorno(retorno):
    """
    Aceita funções que retornem:
    - custo
    - (custo, status)
    - (custo, status, W_values)
    - (custo, status, W_values, K)
    """

    custo = None
    status = "Desconhecido"
    W_values = None
    K = None

    if isinstance(retorno, tuple):
        if len(retorno) >= 1:
            custo = retorno[0]
        if len(retorno) >= 2:
            status = retorno[1]
        if len(retorno) >= 3:
            W_values = retorno[2]
        if len(retorno) >= 4:
            K = retorno[3]
    else:
        custo = retorno
        status = "Optimal" if retorno is not None else "Sem solução"

    return custo, status, W_values, K


# ==========================================================
# CHAMAR UM CRITÉRIO
# ==========================================================

def resolver_criterio(funcao, num_estados, estado_focal, horizonte):
    retorno = funcao(
        H=horizonte,
        S=num_estados,
        N=N_DECISORES,
        s=estado_focal,
        arquivo_J1=f"J1-{num_estados}est.csv",
        arquivo_J2=f"J2-{num_estados}est.csv",
        arquivo_P1=f"P1-{num_estados}est.csv",
        arquivo_P2=f"P2-{num_estados}est.csv"
    )

    return normalizar_retorno(retorno)


# ==========================================================
# SALVAR TABELAS CSV
# ==========================================================

def salvar_tabelas_csv(num_estados, horizontes, resultados):
    for criterio in CRITERIOS:
        nome_arquivo = os.path.join(
            PASTA_TABELAS,
            f"custos_{criterio.replace(' ', '_')}_{num_estados}est_ate_{horizontes[-1]}_horizontes.csv"
        )

        with open(nome_arquivo, mode="w", newline="") as arquivo:
            escritor = csv.writer(arquivo)

            cabecalho = ["estado"] + [f"h={h}" for h in horizontes]
            escritor.writerow(cabecalho)

            for estado in range(num_estados):
                linha = [estado + 1]

                for h in horizontes:
                    custo = resultados[criterio][estado][h]["custo"]
                    linha.append("" if custo is None else custo)

                escritor.writerow(linha)


# ==========================================================
# GERAR GRÁFICOS
# ==========================================================

def gerar_graficos(num_estados, horizontes, resultados):
    marcadores = {
        "Maximin": "o",
        "Maximin Credível": "s",
        "Maximin com Indiferença": "^",
        "Maximin Oponente Credível": "D",
        "Maximin Total Credível": "X"
    }

    estilos_linha = {
        "Maximin": "--",
        "Maximin Credível": "-",
        "Maximin com Indiferença": "-",
        "Maximin Oponente Credível": "-",
        "Maximin Total Credível": "-"
    }

    ordem_plotagem = [
        "Maximin Credível",
        "Maximin com Indiferença",
        "Maximin Oponente Credível",
        "Maximin Total Credível",
        "Maximin"  # fica por último para aparecer por cima
    ]

    for estado in range(num_estados):
        plt.figure(figsize=(10, 6))

        for criterio in ordem_plotagem:
            custos = []

            for h in horizontes:
                custo = resultados[criterio][estado][h]["custo"]
                custos.append(None if custo is None else custo)

            prioridade = 10 if criterio == "Maximin" else 3
            tamanho_no = 10 if criterio == "Maximin" else 8
            espessura = 3 if criterio == "Maximin" else 2

            plt.plot(
                horizontes,
                custos,
                marker=marcadores.get(criterio, "o"),
                linestyle=estilos_linha.get(criterio, "-"),
                markersize=tamanho_no,
                linewidth=espessura,
                label=criterio,
                zorder=prioridade
            )

        plt.xlabel("Horizonte")
        plt.ylabel("Custo ótimo")
        plt.title(f"Custos Maxmin - Estado {estado + 1} - Conflito com {num_estados} estados")
        plt.xticks(horizontes)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=8, frameon=True)
        plt.tight_layout()

        nome_png = os.path.join(
            PASTA_GRAFICOS,
            f"grafico_estado_{estado + 1}_{num_estados}est_ate_{horizontes[-1]}_horizontes.png"
        )

        plt.savefig(nome_png, dpi=300)
        plt.close()


# ==========================================================
# GERAR RELATÓRIO DOCX
# ==========================================================

def gerar_relatorio_txt(num_estados, horizontes, resultados, tempo_total):

    K = carregar_preferencias_originais(num_estados)
    preferencias_originais = preferencias_a_partir_de_K(K)

    nome_txt = os.path.join(
        PASTA_RELATORIOS,
        f"relatorio_Maxmin_{num_estados}est_ate_{horizontes[-1]}_horizontes.txt"
    )

    with open(nome_txt, "w", encoding="utf-8") as f:

        f.write("="*70 + "\n")
        f.write(f"RELATÓRIO MAXMIN - CONFLITO COM {num_estados} ESTADOS\n")
        f.write("="*70 + "\n\n")

        f.write(f"Horizonte máximo: {horizontes[-1]}\n")
        f.write(f"Tempo total: {tempo_total:.2f} segundos\n")
        f.write(f"Tempo total: {tempo_total/60:.2f} minutos\n\n")

        f.write("="*70 + "\n")
        f.write("PREFERÊNCIAS ORIGINAIS\n")
        f.write("="*70 + "\n\n")

        for i, pref in preferencias_originais.items():
            f.write(f"P_{i+1}: {pref}\n")

        f.write("\n")
        f.write("="*70 + "\n")
        f.write("PREFERÊNCIAS GERADAS\n")
        f.write("="*70 + "\n")

        for estado in range(num_estados):

            f.write(f"\n\n########## ESTADO FOCAL s = {estado+1} ##########\n")

            for h in horizontes:

                f.write(f"\n----- Horizonte h = {h} -----\n")

                for criterio in CRITERIOS:

                    item = resultados[criterio][estado][h]

                    custo = item["custo"]
                    status = item["status"]
                    W_values = item["W_values"]

                    f.write(f"\nCritério: {criterio}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"Custo: {custo}\n")

                    if criterio == "Maximin com Indiferença":
                        preferencias_novas = preferencias_a_partir_de_W(W_values, permitir_empate=True)
                    else:
                        preferencias_novas = preferencias_a_partir_de_W(W_values, permitir_empate=False)

                    if preferencias_novas is None:
                        f.write("Preferências não retornadas.\n")
                    else:
                        for i, pref in preferencias_novas.items():
                            f.write(f"P'_{i+1}: {pref}\n")


# ==========================================================
# RODAR UM CONFLITO
# ==========================================================

def rodar_conflito(num_estados, H_max):
    horizontes = list(range(1, H_max + 1))

    resultados = {
        criterio: {
            estado: {}
            for estado in range(num_estados)
        }
        for criterio in CRITERIOS
    }

    print(f"\nRodando conflito com {num_estados} estados...")
    inicio = time.time()

    for estado in range(num_estados):
        print(f"\nEstado focal s = {estado + 1}")

        for h in horizontes:
            print(f"  Horizonte h = {h}")

            for criterio, funcao in CRITERIOS.items():
                print(f"    Critério: {criterio}")

                try:
                    custo, status, W_values, K = resolver_criterio(
                        funcao,
                        num_estados,
                        estado,
                        h
                    )
                except Exception as erro:
                    custo = None
                    status = f"Erro: {erro}"
                    W_values = None

                resultados[criterio][estado][h] = {
                    "custo": custo,
                    "status": status,
                    "W_values": W_values
                }

                print(f"      status = {status}, custo = {custo}")

    fim = time.time()
    tempo_total = fim - inicio

    salvar_tabelas_csv(num_estados, horizontes, resultados)
    gerar_graficos(num_estados, horizontes, resultados)
    gerar_relatorio_txt(num_estados, horizontes, resultados, tempo_total)

    print(f"\nConflito com {num_estados} estados finalizado.")
    print(f"Tempo total: {tempo_total:.2f} segundos")


# ==========================================================
# EXECUTAR TODOS OS CONFLITOS
# ==========================================================

for num_estados in H_por_conflito:
    rodar_conflito(num_estados, H_por_conflito[num_estados])

print("\nProcesso finalizado.")