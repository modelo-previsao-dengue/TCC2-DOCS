# Rastreabilidade dos números da monografia

Cada número do texto sai de um arquivo versionado ou, quando indicado, da saída de um
comando reproduzível. Os caminhos abaixo são relativos
ao repositório [MODELO-PREVISAO](https://github.com/modelo-previsao-dengue/MODELO-PREVISAO),
no commit **`07eb3e3`** (branch `feat/retreino-na-main`, PR #2), exceto quando indicado
`monografia/`, que é este repositório.

Para regenerar as figuras novas e `dados/fatos_derivados.json`:

```bash
/caminho/para/MODELO-PREVISAO/.venv/bin/python scripts/gerar_figuras.py --modelo-previsao /caminho/para/MODELO-PREVISAO
```

Para regenerar os relatórios da pipeline (scripts 20–33): `scripts/rodar_v3.sh` no MODELO-PREVISAO.

## Metodologia (Capítulo 3)

| Número no texto | Fonte |
|---|---|
| 5.570 municípios, 137 mesorregiões, 700 estações, 1–31 estações por mesorregião (mediana 4) | `data/model_ready_v3/20_mapping_report.json` |
| Soma das notificações por mesorregião = Gold, 2018–2026 | `data/model_ready_v3/21_sinan_meso_report.json` (`notificacoes_por_ano`); a comparação com o Gold é a validação impressa por `python scripts/21_aggregate_sinan_mesorregiao.py` |
| Cobertura climática 90,1% e por ano (80,0% a 97,8%) | `data/model_ready_v3/23_integration_report.json` |
| 4.031 fragmentos de virada de ano no INMET | saída de `python scripts/inmet_weekly_aggregate.py --years 2018-2026` (linha "parciais -> semanas-estacao"); não há arquivo versionado com esse número |
| 60.554 linhas, 442 semanas por mesorregião | `data/model_ready_v3/24_lags_report.json`; verificação `check_contiguous` do script 24 |
| Treino 28.633 / validação 7.261 / teste 16.988 linhas; cobertura 89,4% / 92,7% / 89,4% | `data/model_ready_v3/26_splits_v3_report.json` |
| 266 atributos (110 SINAN, 12 brutos, 96 defasagens, 24 médias, 24 anomalias) | `data/model_ready_v3/26_splits_v3_report.json`, `feature_schema_v3.csv` |
| Classes de risco: 52,9% baixo, 12,1% muito alto (série completa) | `data/model_ready_v3/26_splits_v3_report.json` (`classes`) |
| Climatologia das anomalias 2019–2022 | `data/model_ready_v3/25_anomalias_report.json` |
| Hiperparâmetros do XGBoost | `scripts/27_train_regression_v3.py` (`XGB_PARAMS`) |
| 2024 ≈ 6,5 milhões; 2019 ≈ 2,3 milhões de notificações | `data/model_ready_v3/21_sinan_meso_report.json` (`notificacoes_por_ano`) |

## Resultados (Capítulo 4)

| Número no texto | Fonte |
|---|---|
| Tabela 5, coluna "Antes" | relatórios `data/model_ready_v3/2*_*.json` no commit `5721f8a` (main após o PR #1) |
| Tabela 5, coluna "Depois" | relatórios `27`, `28`, `30` e `31` em `data/model_ready_v3/` |
| Inflação do vazamento no rótulo (F1 +0,004 a +0,107; AUC +0,001 a +0,074) | `docs/inflacao_vazamento.csv` |
| Tabela 6 (baselines e XGBoost no teste) | `models/baselines_v3/comparison.csv`, `data/model_ready_v3/33_baselines_v3_report.json` |
| Tabela 7 (por ano), 36% e 90% no topo de 2024, previsto/real | `monografia/dados/fatos_derivados.json` (`por_ano`) |
| Ganhos do clima e testes t (A×B, A×C, B×C) | `data/model_ready_v3/27_regression_v3_report.json` |
| Tabela 8 (walk-forward) | `data/model_ready_v3/31_walkforward_v3_report.json` |
| 22 de 27 UFs, 103 de 137 mesorregiões | `monografia/dados/fatos_derivados.json` |
| Tabela 9 (data blindness) | `data/model_ready_v3/28_blindness_v3_report.json` |
| SHAP (ordem, contribuições médias, 9 no top 30) e Tabela 10 (limiares) | `data/model_ready_v3/30_shap_v3_report.json` |
| Tabela 11 (classificação) | `data/model_ready_v3/29_classification_v3_report.json` e `33_baselines_v3_report.json` |
| Surto binário (0,72–0,74; 0,83; 0,85) | `docs/resultados_surto_binario.md` (variante `media`) |
| Recorte do DF | `monografia/dados/fatos_derivados.json` (`distrito_federal`) |
| Tabela 12 (experimento complementar) | `docs/resultados_modelos_e_baselines.md` |

## Figuras

| Figura | Origem |
|---|---|
| `fig_baselines_vs_xgboost.png`, `fig_serie_nacional_teste.png`, `fig_cobertura_inmet_ano.png` | `monografia/scripts/gerar_figuras.py` |
| `fig_v3_regression_delta_mesorregiao.png` | `scripts/27_train_regression_v3.py` |
| `fig_v3_blindness_comparison.png` | `scripts/28_train_blindness_v3.py` |
| `fig_v3_shap_beeswarm.png` | `scripts/30_explain_shap_v3.py` |

## Pendência

Quando o PR #2 do MODELO-PREVISAO for mergeado, atualizar o commit de referência
acima para o commit de merge na `main`.
