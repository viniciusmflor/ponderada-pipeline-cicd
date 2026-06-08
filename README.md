# Ponderada CI/CD — Análise de Pipeline

**Autor:** Vinicius Maciel Flor
**Repositório:** [viniciusmflor/ponderada-pipeline-cicd](https://github.com/viniciusmflor/ponderada-pipeline-cicd)
**Branch:** [`experimento-cicd`](https://github.com/viniciusmflor/ponderada-pipeline-cicd/tree/experimento-cicd)
**Workflow:** [`.github/workflows/ci.yml`](https://github.com/viniciusmflor/ponderada-pipeline-cicd/blob/experimento-cicd/.github/workflows/ci.yml)

Experimento de instrumentação e análise de pipeline CI/CD com GitHub Actions.

---

## Projeto

API FastAPI (Python 3.12) com testes pytest, baseado no projeto [ponderada-testes-ovidio](https://github.com/viniciusmflor/ponderada-testes-ovidio). A API implementa endpoints de notas fiscais com bugs intencionais (v1) e correções (v2) para volumetria e segurança.

### Stack

- **Backend:** FastAPI 0.115 + SQLAlchemy 2.0 + Pydantic 2.9
- **Testes:** pytest 8.3 (47 testes: volumetria, segurança, sintéticos, string)
- **Lint:** flake8 7.1
- **CI:** GitHub Actions (ubuntu-latest, Python 3.12)
- **Coleta:** Python com `requests`, `pandas`, `matplotlib`

---

## Pipeline CI/CD

O workflow [`.github/workflows/ci.yml`](https://github.com/viniciusmflor/ponderada-pipeline-cicd/blob/experimento-cicd/.github/workflows/ci.yml) contém:

1. **Lint** — checkout, setup-python, cache pip, instalação de dependências, flake8
2. **Test** — checkout, setup-python, cache pip, instalação, pytest com JUnit XML, geração de métricas, upload de artefato

---

## Experimento — 24 execuções

24 execuções com variações controladas:

| # | Variação | Commit | Resultado | Duração |
|---|---|---|---|---|
| 1 | Setup inicial | `58fcc84` | failure | 18s |
| 2 | Cache frio (rerun) | `439aacd` | failure | 17s |
| 3 | Cache quente (rerun) | `d8a15e1` | failure | 15s |
| 4 | +1 teste falhando | `08cf188` | failure | 17s |
| 5 | Corrigir teste | `3084f2d` | failure | 19s |
| 6 | +20 testes sintéticos | `6a1ea93` | failure | 17s |
| 7 | +5 testes lentos | `26372ff` | failure | 17s |
| 8 | Erro de lint proposital | `3c7b33a` | failure | 19s |
| 9 | Corrigir lint (utils.py) | `ec5689c` | failure | 18s |
| 10 | Desabilitar cache | `0ca4bb6` | failure | 20s |
| 11 | Reabilitar cache | `fb64ffe` | failure | 16s |
| 12 | Jobs paralelos | `36c7d2b` | failure | 31s |
| 13 | Voltar sequencial | `99338de` | failure | 19s |
| 14 | 1 job único | `68e708a` | failure | 16s |
| 15 | Restaurar 2 jobs | `3e47ebd` | failure | 16s |
| 16 | Remover lentos | `850ff33` | failure | 14s |
| 17 | **Fix imports F401** | `cb2b75a` | **success** | 47s |
| 18 | Rerun validação | `c6353eb` | **success** | 44s |
| 19 | +10 testes string | `9538fd4` | **success** | 42s |
| 20 | +5 testes lentos | `69672f5` | **success** | 49s |
| 21 | Jobs paralelos | `4a5f123` | **success** | 32s |
| 22 | Voltar sequencial | `4398d28` | **success** | 43s |
| 23 | Fix métricas JUnit | `8d9f82c` | **success** | 40s |
| 24 | Rerun final | `7e95d80` | **success** | 39s |

> As 16 primeiras runs falharam por erro metodológico: imports não usados (F401) no código base que não foram removidos antes de iniciar as variações. Detalhes no [relatório](analytics/RELATORIO.md#51-erro-metodológico-imports-f401-contaminaram-16-runs).

---

## Gráficos

### 1. Tempo total do pipeline por execução

![Tempo total do pipeline](analytics/charts/01_tempo_total_pipeline.png)

Runs com sucesso (verde): 32-49s. Runs com falha (vermelho): 14-31s (truncadas no lint).

### 2. Duração por job (empilhado)

![Duração por job](analytics/charts/02_duracao_por_job.png)

Nas runs com sucesso: lint ~16-18s + test ~18-25s. Run #21 (paralela) é a mais rápida.

### 3. Taxa de sucesso e falha

![Taxa sucesso/falha](analytics/charts/03_taxa_sucesso_falha.png)

8/24 success (33%) vs 16/24 failure (67%). Alta taxa de falha por erro metodológico.

### 4. Quantidade de testes vs duração

![Testes vs duração](analytics/charts/04_testes_vs_duracao.png)

Runs com 47 testes (corrigidas): ~39-40s. Dados limitados por bug na coleta de métricas.

### 5. Distribuição de duração por step

![Boxplot steps](analytics/charts/05_boxplot_duracao_steps.png)

`Instalar dependencias` é o gargalo (~9s mediana). `Executar flake8` consistentemente ~1s.

---

## Principais achados

- **Paralelismo reduziu 25%** do tempo (43s → 32s)
- **Testes lentos adicionaram ~8s** ao pipeline (5 testes com 500ms sleep)
- **pip install é o gargalo** (~9s mediana, maior step individual)
- **Lint dá feedback em <20s** quando falha
- **Erro metodológico contaminou 16 runs** (imports F401 não removidos)
- **Regex na coleta de métricas falhou** (corrigido com JUnit XML)

---

## Métricas e scripts

| Arquivo | Descrição |
|---------|-----------|
| [`analytics/collect_metrics.py`](analytics/collect_metrics.py) | Script de coleta via GitHub API |
| [`analytics/generate_charts.py`](analytics/generate_charts.py) | Geração de gráficos com matplotlib |
| [`analytics/metrics.csv`](analytics/metrics.csv) | Base de dados (355 linhas, 24 runs) |
| [`analytics/charts/`](analytics/charts/) | 5 gráficos PNG |
| [`analytics/RELATORIO.md`](analytics/RELATORIO.md) | Relatório técnico completo |
| [`analytics/requirements.txt`](analytics/requirements.txt) | Dependências Python para analytics |

---

## Estrutura do projeto

```
ponderada-pipeline-cicd/
├── .github/workflows/ci.yml       ← Pipeline CI/CD
├── .flake8                         ← Configuração lint
├── requirements.txt                ← Dependências do projeto
├── app/
│   ├── __init__.py
│   ├── database.py                 ← Configuração SQLAlchemy
│   ├── main.py                     ← API FastAPI
│   ├── models.py                   ← Modelos ORM
│   ├── schemas.py                  ← Schemas Pydantic
│   └── utils.py                    ← Utilitários
├── tests/
│   ├── conftest.py                 ← Fixtures pytest (SQLite)
│   ├── test_01_volumetria.py       ← 7 testes de paginação
│   ├── test_02_falha_proposital.py ← 1 teste (corrigido)
│   ├── test_03_sinteticos.py       ← 20 testes aritméticos
│   ├── test_04_seguranca.py        ← 9 testes de segurança
│   └── test_06_extras.py           ← 10 testes de string
├── analytics/
│   ├── collect_metrics.py          ← Script de coleta
│   ├── generate_charts.py          ← Script de visualização
│   ├── requirements.txt
│   ├── metrics.csv                 ← Base de dados
│   ├── charts/                     ← 5 gráficos PNG
│   └── RELATORIO.md                ← Relatório técnico
└── README.md                       ← Este arquivo
```

---

## Como reproduzir

### 1. Clonar o repositório

```bash
git clone https://github.com/viniciusmflor/ponderada-pipeline-cicd.git
cd ponderada-pipeline-cicd
git checkout experimento-cicd
```

### 2. Rodar os testes localmente

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### 3. Coletar métricas das execuções

```bash
cd analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_seu_token
export REPO="viniciusmflor/ponderada-pipeline-cicd"
python3 collect_metrics.py --out metrics.csv
```

### 4. Gerar gráficos

```bash
python3 generate_charts.py --csv metrics.csv --outdir charts
```

---

## Referência

Estrutura inspirada em [lucasbrasil9/ponderada_bdd_integracao](https://github.com/lucasbrasil9/ponderada_bdd_integracao/tree/experimento-cicd).
