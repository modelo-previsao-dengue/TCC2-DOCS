# Rastreabilidade dos números da monografia

Cada número do texto sai de um arquivo versionado ou, quando indicado, da saída de um
comando reproduzível. Os caminhos abaixo são relativos
ao repositório [MODELO-PREVISAO](https://github.com/modelo-previsao-dengue/MODELO-PREVISAO),
no commit **`a608385`** (branch `main`, pipeline v4 com o INMET corrigido), exceto quando indicado
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
| 2024 ≈ 6,6 milhões; 2015 ≈ 2,4 milhões (maior ano da série longa); 2019 ≈ 2,3 milhões (maior da janela curta) | `data/model_ready_v4/40_sinan_meso_report.json` (`notificacoes_por_ano`) |
| Correção do mapeamento de colunas INMET (por nome do cabeçalho) | `scripts/inmet_extract_standardize.py`, `data/inmet/bronze/reports/us000_mapeamento_colunas_antes_depois.csv` |
| Escala espacial: distância mediana de 32 km até a estação, 20% dos municípios sem estação a 50 km, 6 (máx. 48) municípios por estação | `data/inmet/bronze/municipio_estacao_mapping.csv` (colunas `distancia_km`, `n_estacoes_50km`, `codigo_wmo`) |
| 1 a 31 estações por mesorregião (mediana 4) | `data/model_ready_v3/20_mapping_report.json` |
| Número efetivo de árvores (78 a 517) | `data/model_ready_v4/46_regression_v4_report.json` (`best_iteration`) |

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
| Classificação: F1 macro 0,50 → 0,59 (janela curta → série longa, clima enriquecido) | `data/model_ready_v4/54_classification_v4_report.json` |
| Baselines no teste da v4 (Tabela de desempenho no teste), desempenho por ano, previsto/real, topo de 5% | `data/model_ready_v4/57_avaliacao_modelos_salvos_v4_report.json` (`teste_agregado`, `por_ano`), gerado por `scripts/57_avaliacao_modelos_salvos_v4.py` |
| Métricas de momento: pico a até 2 semanas, erro mediano e médio (179 temporadas), acerto de direção (10.367 semanas) | mesmo relatório 57 (`momento_pico`, `direcao`) |
| Recorte do DF (117 semanas, Tabela do DF) e 277 mil notificações em 2024 | mesmo relatório 57 (`distrito_federal`) |
| Clima melhora em 23 de 27 UFs e 99 de 137 mesorregiões; série longa melhora 118 mesorregiões | `models/regression_v4/metrics_por_uf_v4.csv`, `metrics_por_mesorregiao_v4.csv`; contagem em `monografia/dados/fatos_derivados.json` |
| Blindness v4: Δ R²_log completo +0,007, atraso 4w +0,007, atraso 8w +0,006, só clima 0,399 | `data/model_ready_v4/56_complementos_v4_report.json` (`blindness_B`) |
| Alertas v4: B_enriq F1 macro 0,717, persistência 0,650, classificador 0,585 | mesmo relatório 56 (`alertas_por_limiar`) |
| Momento v4: B_enriq pico ±2sem 48,6%, erro médio −0,44 sem; direção 82,0% | mesmo relatório 56 (`momento`, `direcao`) |

## Figuras

| Figura | Origem |
|---|---|
| `figuras/resultados/fig_baselines_vs_xgboost.png`, `fig_serie_nacional_teste.png` | `monografia/scripts/gerar_figuras.py` (lê o relatório 57). `fig_baselines_vs_xgboost.png` não é usada desde 25/11: substituída por `resultados/fig_baselines_v4.png` |
| `fig_v4_variante_comparison.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: substituída por `resultados/fig_variantes.png`) |
| `fig_v4_r2_by_year.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_walkforward.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: substituída por `resultados/fig_walkforward.png`) |
| `fig_v4_learning_curve.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: substituída por `resultados/fig_curva_aprendizado.png`) |
| `fig_v4_data_drift_psi.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: substituída por `resultados/fig_psi_por_ano.png`) |
| `fig_v4_shap_comparison.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: não é o modelo realista; substituída por `resultados/fig_shap_realista.png`) |
| `fig_v4_cls_f1_comparison.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: valores anteriores ao relatório 54 atual; substituída por `resultados/fig_f1_por_classe.png`) |
| `fig_v4_confusion_matrix.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_delta_mesorregiao_B_vs_A.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: valores anteriores às correções) |
| `fig_v4_gain_comparison.png` | `scripts/53_generate_tcc_outputs.py` |
| `fig_v4_inmet_coverage.png` | `scripts/53_generate_tcc_outputs.py` (não usada desde 25/11: gerada antes da correção dos anos ausentes do INMET) |
| `resultados/fig_cobertura_inmet.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/42_integration_report.json` |
| `resultados/fig_delta_serie_longa.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `models/regression_v4/metrics_por_mesorregiao_v4.csv` |
| `resultados/fig_curva_aprendizado.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/51_learning_curve_report.json` |
| `resultados/fig_psi_por_ano.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `models/regression_v4/data_drift_psi_v4.csv` |
| `resultados/fig_variantes.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/46_regression_v4_report.json` |
| `resultados/fig_walkforward.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/47_walkforward_v4_report.json` |
| `resultados/fig_f1_por_classe.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/54_classification_v4_report.json` |
| `resultados/fig_baselines_v4.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir dos relatórios 57, 58 e 59 em `data/model_ready_v4/` (baselines ingênuos, XGBoost realista, climatologia e Ridge) |
| `resultados/fig_shap_realista.png` | `monografia/scripts/gerar_figuras.py --so-novas`, a partir de `data/model_ready_v4/58_vazamento_temporal_report.json` (`shap_top10` dos modelos completo e realista) |

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
| `scripts/40_aggregate_sinan_full.py` | Agregação SINAN por mesorregião |
| `scripts/41_aggregate_inmet_full.py` | Agregação INMET por mesorregião (mapeamento corrigido) |
| `scripts/42_integrate_full.py` | Integração SINAN + INMET |
| `scripts/43_feature_eng_lags_v4.py` | Engenharia de atributos (defasagens, médias móveis) |
| `scripts/44_feature_eng_anomalias_v4.py` | Anomalias climáticas |
| `scripts/45_prepare_splits_v4.py` | Divisão treino/validação/teste |
| `scripts/46_train_regression_v4.py` | Treinamento regressão (9 combinações) |
| `scripts/47_walkforward_v4.py` | Validação walk-forward (36 modelos) |
| `scripts/48_shap_importance_v4.py` | Interpretação SHAP |
| `scripts/49_optuna_tuning_v4.py` | Otimização Optuna (30 trials) |
| `scripts/50_data_drift_analysis.py` | Análise de drift (PSI) |
| `scripts/51_learning_curve.py` | Curva de aprendizado |
| `scripts/52_compile_final_v4.py` | Compilação de resultados |
| `scripts/53_generate_tcc_outputs.py` | Geração de figuras e tabelas para a monografia |
| `scripts/54_train_classification_v4.py` | Classificação em níveis de risco |
| `scripts/55_build_dashboard_v4.py` | Atualização do dashboard Streamlit |
| `scripts/56_complementos_v4.py` | Baselines com retreino, blindness (4 cenários), alertas por limiar, momento/direção, variação entre sementes |
| `scripts/57_avaliacao_modelos_salvos_v4.py` | Baselines, métricas por ano, métricas de momento e recorte do DF com os modelos salvos (sem retreino) |

## Pendências

- `scripts/57_avaliacao_modelos_salvos_v4.py` precisa ser commitado no MODELO-PREVISAO para que o relatório 57 fique versionado.
- Data de defesa e membros da banca: `informacoes.tex` linhas 18-20 (dependem do orientador).
