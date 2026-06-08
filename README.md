# Ponderada CI/CD — Análise de Pipeline

Experimento de instrumentação e análise de pipeline CI/CD com GitHub Actions.

## Projeto

API FastAPI (Python 3.12) com testes pytest, baseado no projeto [ponderada-testes-ovidio](https://github.com/viniciusmflor/ponderada-testes-ovidio). Pipeline com lint (flake8) e testes automatizados.

## Pipeline CI/CD

O workflow `.github/workflows/ci.yml` contém:

1. **Lint** — instalação de dependências + flake8
2. **Test** — instalação + pytest com geração de métricas JUnit XML
3. **Artefato** — upload de `test-results.xml` e `test-metrics.json`

## Experimento

24 execuções com variações controladas:

- Testes passando/falhando
- Aumento de volume de testes (+20 sintéticos, +10 string)
- Testes lentos artificiais (~500ms cada)
- Cache habilitado/desabilitado
- Jobs paralelos vs sequenciais
- Erros de lint propositais + recovery

## Métricas e Gráficos

- **Script de coleta:** `analytics/collect_metrics.py` (consulta GitHub API)
- **Script de gráficos:** `analytics/generate_charts.py` (matplotlib + pandas)
- **Base de dados:** `analytics/metrics.csv`
- **Gráficos:** `analytics/charts/`
- **Relatório:** `analytics/RELATORIO.md`

## Como reproduzir

```bash
git clone https://github.com/viniciusmflor/ponderada-pipeline-cicd.git
cd ponderada-pipeline-cicd
git checkout experimento-cicd

# Coletar métricas
cd analytics
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_seu_token
export REPO="viniciusmflor/ponderada-pipeline-cicd"
python3 collect_metrics.py --out metrics.csv
python3 generate_charts.py
```

## Referência

Estrutura inspirada em [lucasbrasil9/ponderada_bdd_integracao](https://github.com/lucasbrasil9/ponderada_bdd_integracao/tree/experimento-cicd).
