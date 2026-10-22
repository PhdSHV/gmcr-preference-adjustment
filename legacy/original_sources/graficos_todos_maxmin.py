import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from custo_maxmin import custo_maxmin
from custo_maxmin_credivel import custo_maxmin_credivel
from custo_maxmin_indiferenca import custo_maxmin_indiferenca
from custo_maxmin_oponente_credivel import custo_maxmin_oponente_credivel
from custo_maxmin_total_credivel import custo_maxmin_total_credivel

horizontes = list(range(1, 8))
total_estados = 5
total_decisores = 2
estado_focal = 1

funcoes_custo = {
    "Maximin": custo_maxmin,
    "Maximin com indiferença": custo_maxmin_indiferenca,
    "Maximin credível": custo_maxmin_credivel,
    "Maximin com oponente credível": custo_maxmin_oponente_credivel
   # "Maximin Total credível": custo_maxmin_total_credivel
}


custos_por_funcao = {}

# =========================
# Cálculo dos custos
# =========================
for nome, func in funcoes_custo.items():
    custos = []
    for h in horizontes:
        custo = func(
            H=h,
            S=total_estados,
            N=total_decisores,
            s=estado_focal,
            arquivo_J1="J1-5est.csv",
            arquivo_J2="J2-5est.csv",
            arquivo_P1="P1-5est.csv",
            arquivo_P2="P2-5est.csv"
        )
        custos.append(int(round(custo)))
    custos_por_funcao[nome] = custos

# =========================
# Plot
# =========================
plt.figure(figsize=(8, 5))
ax = plt.gca()

estilos = {
    "Maximin": dict(color="tab:blue", linestyle=":"),
    "Maximin com indiferença": dict(color="tab:orange", linestyle=":"),
    "Maximin credível": dict(color="tab:green", linestyle=":"),
    "Maximin com oponente credível": dict(color="tab:red", linestyle=":"),
}

offset = {
    "Maximin": -0.06,
    "Maximin com indiferença": 0.03,
    "Maximin credível": -0.03,
    "Maximin com oponente credível": 0.06
}

for nome, custos in custos_por_funcao.items():
    plt.plot(
        horizontes,
        [c + offset[nome] for c in custos],
        marker='o',
        linewidth=2,
        label=nome,
        zorder=3,
        **estilos[nome]
    )


ax.spines['bottom'].set_zorder(1)
ax.set_ylim(bottom=0)
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
plt.xticks(horizontes)

# Caso especial: todas as curvas constantes
todos_os_custos = [c for lista in custos_por_funcao.values() for c in lista]
if min(todos_os_custos) == max(todos_os_custos):
    valor = todos_os_custos[0]
    ax.set_ylim(0, max(1, valor + 1))
    ax.set_yticks(range(0, valor + 2))

plt.xlabel("Horizonte h")
plt.ylabel(f"Custo para tornar o estado {estado_focal} estável")
plt.title(f"Custo × Horizonte (estado focal {estado_focal})")
plt.legend()
plt.grid(True)

nome_arquivo = (
    f"grafico_comparativo_{total_estados}_estados_"
    f"estado_{estado_focal}.png"
)
plt.savefig(nome_arquivo, dpi=300)
plt.show()
