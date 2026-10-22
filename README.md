[README.md](https://github.com/user-attachments/files/33823787/README.md)
# gmcr-preference-adjustment# Ajustes Ótimos de Preferências no GMCR

Código-fonte e roteiro de reprodução dos resultados computacionais da tese **“Ajustes Ótimos de Perfis de Preferências Transitivas no Modelo de Grafo para Resolução de Conflitos”** (Hugo Victor Silva, 2026).

O projeto reúne modelos de Programação Linear Inteira/Mista para o Problema de Ajuste de Preferências no Graph Model for Conflict Resolution (GMCR), contemplando os conceitos clássicos Nash, GMR, SMR, SEQ e SSEQ, a estabilidade de horizonte limitado `L_h` e a família Maximin.

## Estrutura

```text
data/                       matrizes de acessibilidade (J) e preferência (P)
expected_results/           valores publicados nas Tabelas 3 a 11 da tese
legacy/original_sources/    arquivos originais do ZIP, sem alteração das formulações
scripts/                    comandos parametrizados de reprodução e verificação
src/gmcr_adjustment/        funções reutilizáveis para L_h e família Maximin
results/                    saídas geradas localmente (ignoradas pelo Git)
```

As duas instâncias incluídas são:

- `nuclear_5_states`: confronto nuclear simplificado, 5 estados e 2 decisores;
- `cuban_missile_crisis_12_states`: crise dos mísseis cubanos, 12 estados e 2 decisores.

Em cada pasta de dados, `J1.csv` e `J2.csv` são matrizes de acessibilidade; `P1.csv` e `P2.csv` são matrizes binárias de preferência.

## Instalação

Recomenda-se Python 3.10–3.12. Crie um ambiente virtual e instale o projeto:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

O solver padrão recomendado é o **CBC**, normalmente disponibilizado pelo pacote PuLP. O IBM ILOG CPLEX também pode ser usado quando estiver instalado e acessível no `PATH`.

Para conferir os solvers detectados:

```bash
python -c "import pulp; print(pulp.listSolvers(onlyAvailable=True))"
```

## Reprodução rápida

Para executar todo o roteiro (as instâncias de 12 estados podem demandar mais tempo):

```bash
python scripts/reproduce_all.py --solver cbc
```

Os comandos abaixo permitem executar cada grupo separadamente.

### 1. Conceitos clássicos — Tabelas 3 e 4

Os modelos clássicos foram mantidos exatamente como fontes legados. O script abaixo cria cópias temporárias, ajusta apenas a instância/estado focal e executa cada formulação isoladamente.

```bash
python scripts/reproduce_classical.py --instance 5 --criteria all --states all --solver cbc
python scripts/reproduce_classical.py --instance 12 --criteria all --states all --solver cbc
```

Saídas:

```text
results/classical/classical_nuclear_5_states.csv
results/classical/classical_cuban_missile_crisis_12_states.csv
```

Execuções parciais também são possíveis:

```bash
python scripts/reproduce_classical.py --instance 12 --criteria nash,gmr --states 9,10,11 --solver cbc
```

Os estados informados na linha de comando são numerados de **1** até `|S|`; internamente os scripts usam índices iniciados em zero.

### 2. Estabilidade de horizonte limitado `L_h` — Tabelas 5 e 6

```bash
python scripts/reproduce_lh.py --instance 5 --max-horizon 15 --states all --solver cbc
python scripts/reproduce_lh.py --instance 12 --max-horizon 6 --states all --solver cbc
```

Saídas:

```text
results/limited_horizon/lh_nuclear_5_states.csv
results/limited_horizon/lh_cuban_missile_crisis_12_states.csv
results/limited_horizon/lh_*.png
```

### 3. Família Maximin — Tabelas 7 a 11 e Figuras 5–6

```bash
python scripts/reproduce_maximin.py --instance 5 --max-horizon 15 --states all --criteria all --solver cbc
python scripts/reproduce_maximin.py --instance 12 --max-horizon 6 --states all --criteria all --solver cbc
```

Critérios disponíveis:

- `maximin`;
- `focal_credible` (Maximin Focal Credível);
- `opponent_credible` (Maximin Oponente Credível);
- `total_credible` (Maximin Total Credível);
- `indifference` (Maximin com Indiferença).

Exemplo reduzido correspondente ao estudo detalhado do estado 9, horizonte 3, no conflito dos mísseis cubanos:

```bash
python scripts/reproduce_maximin.py --instance 12 --max-horizon 3 --states 9 --criteria all --solver cbc
```

Além dos CSV, é gerado um PNG por estado em `results/maximin/<instância>/state_<n>.png`, que fornece os dados gráficos das Figuras 5–6.

Os custos de referência para esse ponto são 16 (Maximin), 16 (Focal Credível), 22 (Oponente Credível), 22 (Total Credível) e 14 (com Indiferença).

## Verificação contra a tese

Após gerar os resultados clássicos e `L_h`, execute:

```bash
python scripts/verify_results.py
```

O verificador compara os CSV produzidos com `expected_results/`. Os arquivos de referência foram transcritos das Tabelas 3–11. Pequenas diferenças nas preferências ótimas podem ocorrer quando existem múltiplas soluções ótimas, mas os custos objetivos devem coincidir.

## Correspondência entre códigos e resultados

| Resultado da tese | Script principal |
|---|---|
| Tabelas 3–4: Nash, GMR, SMR, SEQ e SSEQ | `scripts/reproduce_classical.py` |
| Tabelas 5–6: estabilidade `L_h` | `scripts/reproduce_lh.py` |
| Tabelas 7–11 e dados das Figuras 5–6 | `scripts/reproduce_maximin.py` |
| Formulações e relatórios individuais originais | `legacy/original_sources/` |

## Solvers e reprodutibilidade

- `--solver cbc`: opção aberta e recomendada para reprodução;
- `--solver cplex`: requer instalação/licença do CPLEX;
- `--solver auto`: tenta CPLEX e, em seguida, CBC nos módulos reutilizáveis; nos scripts clássicos preserva a escolha padrão do PuLP.

Os modelos são determinísticos quanto ao valor ótimo. Em presença de ótimos alternativos, o perfil ajustado retornado pode depender do solver ou de sua versão, sem alterar o custo mínimo reportado.

## Observações sobre os fontes originais

Os arquivos de `legacy/original_sources/` foram preservados com seus nomes e configurações originais. Alguns deles:

- assumem que os CSV estão no diretório corrente;
- possuem estado focal e instância fixados no início do arquivo;
- chamam diretamente CPLEX;
- produzem relatórios `.txt` extensos.

Os scripts da pasta `scripts/` foram acrescentados para resolver essas limitações operacionais sem substituir ou reescrever as formulações originais.

## Citação

Use o arquivo `CITATION.cff` para gerar a citação do software no GitHub. A referência acadêmica principal é a tese de Hugo Victor Silva (UFPE, 2026).

## Publicação no GitHub

Consulte [`PUBLISHING.md`](PUBLISHING.md) para os comandos de criação e envio do repositório.
