# Rastreabilidade dos números da monografia

Cada número do texto sai de um arquivo versionado ou, quando indicado, da saída de um
comando reproduzível. Os caminhos abaixo são relativos
ao repositório [MODELO-PREVISAO](https://github.com/modelo-previsao-dengue/MODELO-PREVISAO),
no commit **`eb64c67`** (branch `main`, pipeline v4 completa), exceto quando indicado
`monografia/`, que é este repositório.

Para regenerar os relatórios da pipeline v4 (scripts 40–55):

```bash
cd MODELO-PREVISAO
source .venv/bin/activate
for s in scripts/4*.py scripts/5*.py; do python "$s"; done
```

Os dados corrigidos estão disponíveis em:
- HuggingFace: `pedrolucassantanaf/dengue-tcc2-data`
- Kaggle: `pedrolucassantana` (notebooks públicos)

## Metodologia (Capítulo 3)

| Número no texto | Fonte |
|---|---|
| 5.570 municípios, 137 mesorregiões, ~700 estações | `data/model_ready_v4/40_sinan_meso_report.json`, `41_inmet_meso_report.json` |
| Cobertura climática e por ano | `data/model_ready_v4/42_integration_report.json` |
| Linhas do dataset integrado, semanas por mesorregião | `data/model_ready_v4/43_lags_report.json` |
| Treino / validação / teste splits | `data/model_ready_v4/45_splits_report.json` |
| 266 atributos (110 SINAN, 12 brutos, 96 defasagens, 24 médias, 24 anomalias) | `data/model_ready_v4/45_splits_report.json` |
| Classes de risco (distribuição) | `data/model_ready_v4/45_splits_report.json` |
| Climatologia das anomalias | `data/model_ready_v4/44_anomalias_report.json` |
| Hiperparâmetros do XGBoost | `scripts/46_train_regression_v4.py` (`XGB_PARAMS`) |
| 2024 ≈ 6,5 milhões; 2019 ≈ 2,3 milhões de notificações | `data/model_ready_v4/40_sinan_meso_report.json` |
| Correção do mapeamento de colunas INMET (header-name vs posicional) | `scripts/11_inmet_bronze_to_silver.py`, `data/model_ready_v4/41_inmet_meso_report.json` |

## Resultados (Capítulo 4)

| Número no texto | Fonte |
|---|---|
| 9 combinações (3 variantes × 3 conjuntos de atributos), R²_log, CI95, RMSE, MAE | `data/model_ready_v4/46_regression_v4_report.json` |
| Walk-forward (4 janelas expansíveis, 36 modelos) | `data/model_ready_v4/47_walkforward_v4_report.json` |
| SHAP (top 10 features por variante, 10.000 amostras) | `data/model_ready_v4/48_shap_report.json` |
| Optuna (30 trials, baseline 0,851, best 0,853, não adotado) | `data/model_ready_v4/49_optuna_report.json` |
| PSI drift (185 high, 73 moderate, 182 low) | `data/model_ready_v4/50_drift_report.json` |
| Learning curve (5 janelas, 4 a 22 anos) | `data/model_ready_v4/51_learning_curve_report.json` |
| Resultados finais compilados | `data/model_ready_v4/52_final_results_v4.json` |
| Classificação (F1, AUC, accuracy por classe, 9 combos) | `data/model_ready_v4/54_classification_v4_report.json` |
| Melhor modelo: série longa 22 anos + clima enriquecido, R²_log = 0,890 | `data/model_ready_v4/46_regression_v4_report.json` |
| Série longa vs curta: +0,015 R²_log (p < 10⁻⁴⁶) | `data/model_ready_v4/46_regression_v4_report.json` |
| Ganho do clima: +0,008 R²_log | `data/model_ready_v4/46_regression_v4_report.json` |
| Classificação: F1 macro 0,48 → 0,58 (série longa) | `data/model_ready_v4/54_classification_v4_report.json` |

## Figuras

| Figura | Origem |
|---|---|
| `fig_v4_variante_comparison.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_r2_by_year.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_walkforward.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_learning_curve.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_data_drift_psi.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_shap_comparison.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_cls_f1_comparison.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_confusion_matrix.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_delta_mesorregiao_B_vs_A.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_gain_comparison.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_inmet_coverage.png` | `scripts/53_generate_tcc_outputs.py` |

## Tabelas geradas

| Tabela | Origem |
|---|---|
| `tabelas/tab_v4_regression_comparison.tex` | `scripts/53_generate_tcc_outputs.py` |
| `tabelas/tab_v4_walkforward.tex` | `scripts/53_generate_tcc_outputs.py` |
| `tabelas/tab_v4_classification.tex` | `scripts/53_generate_tcc_outputs.py` |
| `tabelas/tab_v4_r2_by_year.tex` | `scripts/53_generate_tcc_outputs.py` |
| `tabelas/tab_v4_r2_by_flag.tex` | `scripts/53_generate_tcc_outputs.py` |
| `tabelas/tab_v4_statistical_tests.tex` | `scripts/53_generate_tcc_outputs.py` |

## Scripts da pipeline v4

| Script | Função |
|---|---|
| `scripts/40_aggregate_sinan_mesorregiao.py` | Agregação SINAN por mesorregião |
| `scripts/41_inmet_mesorregiao.py` | Agregação INMET por mesorregião (mapeamento corrigido) |
| `scripts/42_integrate_sinan_inmet.py` | Integração SINAN + INMET |
| `scripts/43_create_lags.py` | Engenharia de atributos (defasagens, médias móveis) |
| `scripts/44_create_anomalias.py` | Anomalias climáticas |
| `scripts/45_split_data.py` | Divisão treino/validação/teste |
| `scripts/46_train_regression_v4.py` | Treinamento regressão (9 combinações) |
| `scripts/47_walkforward_v4.py` | Validação walk-forward (36 modelos) |
| `scripts/48_explain_shap.py` | Interpretação SHAP |
| `scripts/49_optuna_v4.py` | Otimização Optuna (30 trials) |
| `scripts/50_drift_analysis.py` | Análise de drift (PSI) |
| `scripts/51_learning_curve.py` | Curva de aprendizado |
| `scripts/52_compile_final_results.py` | Compilação de resultados |
| `scripts/53_generate_tcc_outputs.py` | Geração de figuras e tabelas para a monografia |
| `scripts/54_classification_v4.py` | Classificação em níveis de risco |
| `scripts/55_update_dashboard.py` | Atualização do dashboard Streamlit |
