# PRD: Ajustes na Pipeline de Treinamento — Revisão do Orientador

## Introdução

O orientador (Prof. Fabiano) revisou o TCC2 e apontou problemas no desenho da avaliação que afetam as conclusões principais. Este PRD cobre **apenas os ajustes algorítmicos e de pipeline** que o Pedro vai implementar no repositório MODELO-PREVISAO. Os ajustes de texto da monografia (pergunta de pesquisa, narrativa, forma, referências, legendas, cronograma, apêndices de algoritmos) ficam com o Thiago.

O professor disse: "priorizem, ajustem as mais críticas, reportem as menos críticas e incluam em trabalhos futuros." Este PRD segue essa diretriz — cada US está classificada como:
- **IMPLEMENTAR**: ajuste crítico que muda resultados ou conclusões
- **TRABALHO FUTURO**: ponto válido, mas inviável no prazo — justificar no texto e mover para trabalhos futuros

## Contexto Técnico

- **Pipeline atual**: scripts 40–57 em `MODELO-PREVISAO/scripts/`
- **Dados**: `data/model_ready_v4/` (splits A/B/C, reports JSON)
- **Melhor modelo**: variante B (treino 2001–2022), INMET enriquecido, R²_log = 0,890
- **Teste**: 2024–2026, 16.029 mesorregião-semanas (137 mesorregiões × ~117 semanas)
- **Features**: 266 no total (110 SINAN + 156 INMET). Das 110 SINAN, **96 são da semana t** (proporções clínicas, contagens de classificação, índices compostos) e 14 são defasagens/médias móveis. A contagem bruta `notificacoes` da semana t foi excluída das features (script 45, linha 97)
- **Target**: `notificacoes_t4` = notificações 4 semanas à frente (shift -4)
- **Cobertura climática por ano** (do report 42): 1,9% em 2000, 68% em 2007, >80% a partir de 2008, pico de 98% em 2017–2019
- **SHAP top 5 (modelo B enriquecido)**: `notificacoes_lag_1w` (1.15), `week_of_year_cos` (0.26), `notificacoes_diff_1w` (0.17), **`qt_confirmados_provaveis`** (0.12), `notificacoes_media_movel_2_4w` (0.10)
- **`flag_fonte_inmet`**: removida dos splits (é metadata no script 45), mas está no dataset integrado (`integrated_mesorregiao_v4.parquet`)
- **Definição de "temporada com surto"** (script 56): mesorregião × ano onde `risco_surto_t4.max() >= 3` (percentil 90 do treino). O professor questionou que isso condiciona no desfecho observado

## Objetivos

1. Corrigir o vazamento temporal dos atributos clínicos consolidados da semana t
2. Incluir `notificacoes` da semana t como feature para comparação justa com persistência
3. Adicionar baselines não-ingênuos (climatologia por mesorregião-semana, ridge autorregressivo)
4. Criar controle região+semana para testar se o "cenário só clima" é proxy de localização
5. Reportar métricas escaladas por mesorregião (MASE) em vez de só R² agregado
6. Corrigir teste estatístico (Diebold-Mariano ou bootstrap em blocos)
7. Separar métricas 2024–2025 (consolidadas) das 2024–2026 (com 2026 incompleto)
8. Incluir persistência e regressão como baselines na tabela de classificação
9. Testar se ganho do clima se mantém sem anos de baixa cobertura
10. Recalcular SHAP para o modelo "realista" (sem vazamento temporal)

## Mapeamento: Resultado → Seção da Monografia

Cada US gera dados que alimentam uma seção específica da monografia. Isso guia o Thiago nos ajustes de texto.

| US | Seção afetada | O que muda |
|---|---|---|
| 001–003 | 4.1 (desempenho geral), 4.14 (SHAP), Limitações | Novo modelo "realista" vira resultado principal; modelo atual vira "cenário otimista" |
| 004–005 | 4.1 (tabela baselines), Conclusão | Climatologia e ridge entram na tabela de baselines |
| 006 | 4.9 (blindness/só clima), Conclusão | Controle confirma ou invalida o papel do clima |
| 007 | 4.1, nova subseção ou apêndice | MASE por mesorregião complementa R² agregado |
| 008 | 4.4 (testes estatísticos), todo lugar com p-value | DM substitui teste t; p-values ficam com menos casas |
| 009 | 4.1, 4.5, todas as tabelas | Métricas 2024-2025 viram as principais; 2024-2026 fica como "incluindo dados parciais" |
| 010 | 4.8 (classificação, Tabela 13) | Persistência como baseline de classificação |
| 011 | 4.4 (clima), Limitações | Confirma ou questiona o ganho do clima |
| 012 | 4.14 (SHAP) | Novo SHAP top 10 sem features com vazamento |
| 013 | 4.6 (momento), Conclusão | Métricas de antecedência mais robustas |

## User Stories

---

### Fase 1 — Correção de Vazamento Temporal (IMPLEMENTAR)

O professor chamou isso de "bem importante". É o ajuste mais crítico.

### US-001: Auditar features SINAN da semana t por disponibilidade em tempo real
**Descrição:** Como pesquisador, preciso classificar cada uma das 96 features SINAN da semana t (que não são defasagens) por sua disponibilidade em um cenário operacional de vigilância epidemiológica.

**Contexto do problema:** O microdado SINAN passa por consolidação: a classificação final (confirmado, descartado, inconclusivo) só existe semanas depois da notificação inicial. No momento da notificação, existem: a contagem bruta, dados demográficos (sexo, raça, idade), sintomas iniciais (febre, mialgia, etc.) e o fato de ter sido hospitalizado ou não. Mas NÃO existem: classificação final, critério diagnóstico (clínico/laboratorial), resultado de sorologia, e indicadores de gravidade baseados na evolução (óbito, dengue grave, dengue com sinais de alarme — estes dependem do acompanhamento).

**Acceptance Criteria:**
- [ ] Criar `data/model_ready_v4/feature_availability_audit.json` com 3 listas:
  - `available_realtime`: features disponíveis na notificação inicial
    - Defasagens: `notificacoes_lag_*`, `notificacoes_media_movel_*`, `notificacoes_diff_*`, `notificacoes_pct_change_*`
    - Sazonalidade: `week_of_year_sin`, `week_of_year_cos`
    - Contagem bruta: `notificacoes` (a incluir como feature), `is_zero_notification_week`
    - Demográficos: `prop_sexo_*`, `prop_raca_*`, `idade_media_anos`
    - Sintomas iniciais: `prop_febre`, `prop_mialgia`, `prop_cefaleia`, `prop_artralgia`, `prop_exantema`, `prop_nausea`, `prop_vomito`, `prop_dor_retro`, `prop_dor_costas`, `prop_conjuntvit`, `prop_laco`, `prop_laco_n`
    - Gestante: `prop_gestante`
    - Comorbidades pré-existentes: `prop_diabetes`, `prop_hipertensa`, `prop_auto_imune`, `prop_hematolog`, `prop_hepatopat`, `prop_renal`
    - Atraso: `atraso_notificacao_medio_dias`
  - `delayed_consolidation`: features que dependem de consolidação
    - Classificação: `qt_confirmados_provaveis`, `prop_confirmado_provavel`, `qt_descartados`, `prop_descartado`, `qt_inconclusivos`, `prop_inconclusivo`
    - Critério: `prop_criterio_clinico`, `prop_criterio_clinico_epi`, `prop_criterio_lab`
    - Gravidade/evolução: `qt_dengue_alarme`, `prop_dengue_alarme`, `qt_dengue_grave`, `prop_dengue_grave`, todos os `prop_grav_*` (12 features), `prop_alrm_*` (10 features)
    - Desfecho: `qt_obitos_agravo`, `prop_obito_agravo`, `qt_obitos_outras_causas`, `prop_obito_outras_causas`, `qt_hospitalizados`, `prop_hospitalizado`
    - Hemorrágicos: `prop_mani_hemor`, `prop_epistaxe`, `prop_gengivo`, `prop_metro`, `prop_petequias`, `prop_petequia_n`, `prop_hematura`, `prop_sangram`, `prop_plaq_menor`, `prop_plasmatico`, `prop_leucopenia`
    - Chikungunya: `qt_chikungunya`, `prop_chikungunya`, `prop_artrite`, `prop_acido_pept`
    - Índices compostos: `indice_alarme`, `indice_carga_clinica`, `indice_comorbidades`, `indice_confirmacao`, `indice_desfecho_severo`, `indice_gravidade`, `indice_hemorragico`, `indice_sintomas`
    - Evidência: `prop_evidencia`
  - `ambiguous`: vazio ou com justificativa (a hospitalização pode ser registrada no mesmo dia, mas a evolução posterior é delayed)
- [ ] Para cada feature, incluir campo `justificativa`
- [ ] Contar: quantas features em cada lista

### US-002: Retreinar modelo sem vazamento e com notificações da semana t
**Descrição:** Como pesquisador, preciso treinar modelos com 3 conjuntos de features para quantificar o impacto do vazamento temporal e da inclusão de `notificacoes` da semana t.

**Acceptance Criteria:**
- [ ] Criar script `58_avaliacao_vazamento_temporal.py`
- [ ] Treinar variante B com 3 conjuntos de features:
  1. **Completo** (atual, 266 features) — reprodução do script 46 para conferência
  2. **Realista** (exclui todas as `delayed_consolidation` da US-001, mantém `available_realtime` + INMET enriquecido, **inclui** `notificacoes` da semana t)
  3. **Realista sem notificacoes_t** (igual ao realista mas sem `notificacoes`)
- [ ] Métricas para cada conjunto: R²_log, R²_original, MAE, RMSE no teste agregado
- [ ] Métricas por ano (2024, 2025, 2026 separados)
- [ ] Comparação direta com persistência em cada cenário
- [ ] Gerar report: `data/model_ready_v4/58_vazamento_temporal_report.json`
- [ ] **Decisão no report**: campo `modelo_principal` indicando qual conjunto será o resultado principal da monografia:
  - Se queda realista vs completo < 0,01 R²_log: o vazamento é marginal → reportar como limitação, manter completo como principal
  - Se queda entre 0,01 e 0,03: material → realista vira principal, completo vira "cenário otimista"
  - Se queda > 0,03: grave → realista é o único resultado válido

### US-012: Recalcular SHAP para o modelo realista
**Descrição:** Como pesquisador, preciso do SHAP top 10 do modelo realista para substituir a interpretação atual se `qt_confirmados_provaveis` sair do top 5.

**Acceptance Criteria:**
- [ ] No script 58, calcular SHAP values (10.000 amostras) para o modelo realista
- [ ] Reportar top 10 features por |SHAP| médio
- [ ] Comparar com o SHAP do modelo completo (script 48)
- [ ] Se `qt_confirmados_provaveis` saiu do top 10 no realista: isso confirma o vazamento e o novo SHAP substitui o atual na monografia

---

### Fase 2 — Baselines e Controles (IMPLEMENTAR)

O professor disse: "Sem [baselines não-ingênuos], não se sabe se o XGBoost acrescenta algo sobre modelos simples."

### US-004: Baseline de climatologia por mesorregião-semana
**Descrição:** Como pesquisador, preciso de um baseline sazonal real (média histórica de cada mesorregião na mesma semana epidemiológica) para substituir o "sazonal (ano anterior)" que é "fraco por construção".

**Acceptance Criteria:**
- [ ] Criar script `59_baselines_avancados.py`
- [ ] Para cada mesorregião × semana_epidemiologica: calcular média e mediana das notificações no treino B (2001–2022)
- [ ] Previsão t+4: para a linha (mesorregião m, semana s), a previsão é a média histórica de m na semana s+4
- [ ] Métricas: R²_log, R²_original, MAE, RMSE — no teste agregado e por ano
- [ ] Report: `data/model_ready_v4/59_baselines_avancados_report.json`

### US-005: Baseline de ridge autorregressivo
**Descrição:** Como pesquisador, preciso de uma regressão linear regularizada com as mesmas features disponíveis em tempo real para verificar se o ganho do XGBoost vem da não-linearidade ou das features.

**Acceptance Criteria:**
- [ ] No script 59, treinar `RidgeCV` (sklearn) com as features do modelo **realista** (pós-US-001): defasagens, médias móveis, `notificacoes`, sazonalidade, INMET enriquecido
- [ ] `alphas=[0.01, 0.1, 1, 10, 100]`, validação no val B (2023)
- [ ] Target: `log1p(notificacoes_t4)` para comparabilidade com R²_log
- [ ] Reportar R²_log, R²_original, MAE, RMSE
- [ ] **Interpretação no report**: se Ridge ≈ XGBoost realista (< 0,01 R²_log), documentar — significa que features lineares bastam

### US-006: Controle região+semana para o cenário "só clima"
**Descrição:** Como pesquisador, preciso verificar se o R²_log de 0,399 no cenário "só clima" (script 56) vem do sinal climático real ou apenas da identificação da região e da sazonalidade (professor: "as variáveis climáticas podem estar apenas identificando a região").

**Acceptance Criteria:**
- [ ] No script 59, treinar XGBoost com apenas `cod_mesorregiao` (label encoding — XGBoost nativo lida com categóricas) + `week_of_year_sin` + `week_of_year_cos`
- [ ] Comparar R²_log com:
  - Cenário "só clima" do script 56: R²_log = 0,399
  - Climatologia da US-004
- [ ] **Interpretação**:
  - Controle ≥ 0,399 → clima é proxy de localização/sazonalidade. Conclusão do blindness precisa ser revisada
  - Controle significativamente < 0,399 → clima carrega sinal independente além de localização
- [ ] Treinar também: região+semana+clima (os 3 juntos) para ver o ganho incremental do clima sobre localização
- [ ] Report no JSON do script 59

---

### Fase 3 — Métricas e Testes Corrigidos (IMPLEMENTAR)

### US-007: Métricas por mesorregião e MASE
**Descrição:** Como pesquisador, preciso reportar métricas escaladas por mesorregião para resolver que "R² mistura regiões com ordens de grandeza distintas, então parte do valor vem da diferença de escala" (professor).

**Acceptance Criteria:**
- [ ] Criar script `60_metricas_corrigidas.py`
- [ ] Para cada uma das 137 mesorregiões, calcular (no modelo **realista** e na persistência):
  - R²_log local (só dentro daquela mesorregião)
  - MAE
  - MASE = MAE_modelo / MAE_persistência (< 1 = modelo melhor)
- [ ] Estatísticas resumo do MASE: mediana, média, P25, P75, min, max
- [ ] Contar: em quantas mesorregiões MASE < 1 (modelo vence persistência)
- [ ] Gerar CSV por mesorregião: `models/regression_v4/60_mase_por_mesorregiao.csv`
- [ ] Report: `data/model_ready_v4/60_metricas_corrigidas_report.json`

### US-008: Teste de Diebold-Mariano e bootstrap em blocos
**Descrição:** Como pesquisador, preciso substituir o teste t pareado (inflado por autocorrelação temporal e espacial sobre 16k observações) por testes que respeitem a estrutura dos dados.

**Acceptance Criteria:**
- [ ] No script 60, implementar:
  1. **Diebold-Mariano** com correção de Newey-West (truncation lag = número de semanas no teste ÷ 2, arredondado)
  2. **Bootstrap em blocos** (bloco = mesorregião-ano, 1000 repetições)
- [ ] Comparações a testar:
  - XGBoost realista vs persistência
  - XGBoost realista (com clima) vs XGBoost realista (sem clima) — ganho do clima
  - XGBoost realista vs ridge — ganho da não-linearidade
  - XGBoost realista vs climatologia
- [ ] Loss function: squared error em log1p(y) — consistente com R²_log
- [ ] Reportar: estatística DM, p-value corrigido (máximo 3 casas decimais, como pediu o professor)
- [ ] No bootstrap: IC 95% da diferença de R²_log
- [ ] **Se p-value corrigido do ganho do clima (+0,008) não for significativo**: documentar honestamente — muda a conclusão sobre clima

### US-009: Separar 2026 incompleto
**Descrição:** Como pesquisador, preciso reportar métricas principais sem 2026 (incompleto, ~12 semanas, dados não consolidados).

**Contexto:** O professor disse: "O ano de 2026 está incompleto e não consolidado. Retire-o das métricas principais ou trate-o à parte."

**Acceptance Criteria:**
- [ ] No script 60, todas as métricas reportadas em duas versões:
  - `teste_consolidado`: apenas 2024–2025 (linhas do teste com `ano <= 2025`)
  - `teste_completo`: 2024–2026 (como hoje, para comparação)
- [ ] Contagem de linhas em cada versão
- [ ] O `teste_consolidado` vira a referência principal; o `teste_completo` fica como nota

---

### Fase 4 — Classificação, Cobertura e Pico (IMPLEMENTAR)

### US-010: Persistência e regressão na tabela de classificação
**Descrição:** Como pesquisador, preciso que a tabela de classificação de risco (Tabela 13) inclua baselines para que o leitor saiba se o classificador XGBoost agrega valor.

**Contexto:** No Apêndice A, persistência com limiares tem F1 macro = 0,62, acima do classificador XGBoost (0,585). O próprio apêndice recomenda gerar alertas pela regressão. O professor pediu explicitamente: "Inclua a persistência e a regra sobre a regressão na Tabela 13."

**Acceptance Criteria:**
- [ ] Criar script `61_classificacao_completa.py`
- [ ] Calcular classificação de risco aplicando limiares do treino B a:
  - Persistência (valor de t repetido para t+4)
  - Climatologia (US-004)
  - Regressão XGBoost B realista (previsão numérica → limiares)
  - Classificador XGBoost B (do script 54, para referência)
- [ ] Métricas por método: F1 macro, accuracy, F1 por classe (4 classes)
- [ ] Report: `data/model_ready_v4/61_classificacao_completa_report.json`

### US-011: Retreino sem anos de baixa cobertura climática
**Descrição:** Como pesquisador, preciso testar se o ganho do clima está confundido com a época (anos antigos sem clima × anos recentes com clima).

**Contexto:** O professor disse: "A cobertura climática vai de 1,9% a ~98%. O XGBoost trata ausência como informação, então 'tem clima ou não' pode atuar como proxy do ano. O ganho da série longa e o do clima podem estar parcialmente confundidos."

**Acceptance Criteria:**
- [ ] Criar script `62_controle_cobertura_climatica.py`
- [ ] Treinar 3 variantes:
  1. **B completo** (2001–2022, 157k linhas) — reprodução
  2. **B cobertura alta** (2008–2022, ~15 anos, cobertura > 80%) — com e sem clima
  3. **B só linhas com clima** (2001–2022, apenas linhas com `flag_fonte_inmet == True`) — com e sem clima
- [ ] Para cada: R²_log, ganho do clima (Δ R²_log com vs sem INMET)
- [ ] **Nota**: `flag_fonte_inmet` não está nos splits — carregar do `integrated_mesorregiao_v4.parquet` e fazer merge por ID_COLS
- [ ] Report: `data/model_ready_v4/62_controle_cobertura_report.json`
- [ ] **Interpretação**: se ganho do clima em "B cobertura alta" ≈ ganho em "B completo", o confundimento é menor; se ganho cai, o clima parcialmente é proxy do ano

### US-013: Métrica de antecedência do alerta corrigida
**Descrição:** Como pesquisador, preciso corrigir a métrica de pico que é "enviesada a favor do modelo" (professor) e medir a antecedência real do alerta.

**Contexto:** O professor apontou 3 problemas: (1) o pico da persistência fica 4 semanas atrasado por construção, o que torna a comparação injusta; (2) falta medir a antecedência real (semanas antes do pico que o modelo sinaliza subida); (3) selecionar temporadas pelo risco observado condiciona no desfecho.

**Acceptance Criteria:**
- [ ] No script 60 ou 61, implementar métricas de antecedência corrigidas:
  1. **Semanas de antecipação da subida**: para cada mesorregião-temporada, medir quantas semanas antes do pico real o modelo prevê que a tendência é de alta (definição: previsão > previsão da semana anterior por N semanas consecutivas)
  2. **Comparação com previsor de tendência**: baseline "subida se notificacoes_lag_1w > notificacoes_lag_2w" (tendência observada) — comparar com a subida prevista pelo modelo
  3. **Definição de temporada explícita**: documentar que "temporada com surto" = mesorregião-ano com pelo menos 1 semana no percentil 90 do treino, e que isso condiciona no desfecho observado → mover para limitação
- [ ] Reportar: antecipação mediana do modelo (em semanas antes do pico) vs antecipação do previsor de tendência
- [ ] Remover comparação com persistência na métrica de pico (injusta por construção) e substituir pela comparação com o previsor de tendência

---

## Requisitos Funcionais

- FR-01: Scripts novos seguem o padrão da pipeline v4 (report JSON, XGB_PARAMS, ID_COLS, seed 42)
- FR-02: Reports incluem `tempo_total_s`, parâmetros usados, e versão do conjunto de features
- FR-03: Modelos "realistas" salvos em `models/regression_v4/` com sufixo `_realista`
- FR-04: Seed fixa 42 em todos os treinamentos
- FR-05: Scripts executáveis independentemente (cada um carrega dados próprios)
- FR-06: `PYTHONUNBUFFERED=1` em execuções longas
- FR-07: Baselines comparáveis (mesmas métricas, mesmo teste, mesma escala log1p)
- FR-08: MASE usa persistência como denominador
- FR-09: P-values com no máximo 3 casas decimais significativas (ex: 0.003, não 7.7×10⁻⁴⁷)
- FR-10: Todas as métricas em versão `teste_consolidado` (2024–2025) e `teste_completo` (2024–2026)

## Fora de Escopo (Trabalhos Futuros)

Cada item vai para a seção "Trabalhos Futuros" da monografia com justificativa:

| Item do professor | Justificativa para trabalhos futuros |
|---|---|
| **SARIMA/SARIMAX** | 137 séries × grid search é computacionalmente pesado; o ridge (US-005) serve como proxy linear |
| **Normalização por população (incidência)** | Requer dados de população por mesorregião-ano que não estão na pipeline atual |
| **Canal endêmico** como definição de surto | Requer reprojetar toda a classificação; documentar a escolha dos percentis como limitação |
| **Intervalos de previsão** (regressão quantílica) | Já estava nos trabalhos futuros |
| **Avaliação de usabilidade do dashboard** | Fora do escopo de pipeline; é de interesse para trabalho de continuação |
| **API legado municipal** | Ajuste de texto — remover do corpo ou atualizar (responsabilidade do Thiago) |

**Sobre o SHAP v3 vs v4**: O professor disse que "O SHAP principal (4.15) e os limiares climáticos são da v3". O SHAP no capítulo 4 é da v4 (script 48), mas os limiares climáticos citados na síntese ("temperatura mínima acima de 13,8°C") podem ser da v3. Verificar no texto — se são da v3, substituir pelo SHAP do modelo realista (US-012).

**Sobre reuso do teste**: O professor apontou que o teste serviu para v3, v4, learning curve e PSI, e que "as variantes B e C foram criadas depois de ver resultados anteriores". Declarar como limitação no texto: o desenho experimental não separa um holdout final intocado. Mitigação: as decisões (série longa, clima) foram motivadas pela literatura, não por otimização no teste.

## Considerações Técnicas

### Dependências entre US
```
US-001 → US-002 (auditoria define features do modelo realista)
US-002 → US-005 (ridge usa features realistas)
US-002 → US-007 (MASE calculado sobre modelo realista)
US-002 → US-008 (DM calculado sobre modelo realista)
US-002 → US-012 (SHAP do modelo realista)
US-004 → US-006 (climatologia como referência)
US-004 → US-010 (climatologia na tabela de classificação)
US-006, US-009, US-011, US-013 são independentes
```

### Ordem de execução recomendada
1. **US-001** (auditoria manual, ~30 min)
2. **US-002 + US-012** (script 58: treino + SHAP, ~50 min)
3. **US-004 + US-005 + US-006** (script 59: baselines, ~20 min)
4. **US-007 + US-008 + US-009** (script 60: métricas corrigidas, ~10 min)
5. **US-010** (script 61: classificação, ~15 min)
6. **US-011** (script 62: cobertura climática, ~30 min)
7. **US-013** (dentro do script 60 ou 61: antecedência, ~10 min)

**Total estimado: ~3h de computação**

### Dados necessários
- `data/model_ready_v4/splits_b/train.parquet` (157.413 linhas)
- `data/model_ready_v4/splits_b/val.parquet` (7.261 linhas)
- `data/model_ready_v4/splits_b/test.parquet` (16.029 linhas)
- `data/model_ready_v4/feature_schema_v4.csv` (266 features)
- `data/model_ready_v4/integrated_mesorregiao_v4.parquet` (para `flag_fonte_inmet`)
- `data/model_ready_v4/42_integration_report.json` (cobertura INMET por ano)
- `data/model_ready_v4/feature_availability_audit.json` (gerado pela US-001)

## Métricas de Sucesso

- [ ] Todos os scripts (58–62) executam sem erro e geram reports JSON
- [ ] Modelo "realista" documentado com R²_log e comparado ao atual — diferença quantificada
- [ ] SHAP recalculado para modelo realista — `qt_confirmados_provaveis` não aparece no top 10
- [ ] ≥3 baselines não-ingênuos reportados (climatologia, ridge, controle região+semana)
- [ ] Controle região+semana responde se o "cenário só clima" é proxy de localização
- [ ] Teste DM substitui teste t pareado em todas as comparações
- [ ] MASE mediano < 1 (modelo supera persistência na maioria das mesorregiões)
- [ ] Métricas 2024–2025 separadas das 2024–2026
- [ ] Persistência e regressão aparecem como baselines na tabela de classificação
- [ ] Ganho do clima testado sem confundimento de cobertura

## Questões em Aberto

1. **Sintomas iniciais vs consolidação**: algumas features como `prop_hospitalizado` podem estar disponíveis no mesmo dia (registro de internação) ou semanas depois (evolução do caso). A US-001 coloca como `delayed_consolidation` por conservadorismo — se o orientador discordar, mover para `available_realtime`.
2. **Ridge com features INMET**: o ridge usa INMET enriquecido (266 features) ou só SINAN? Recomendação: testar ambos e reportar — se ridge+INMET ≈ XGBoost, a contribuição do XGBoost é questionável.
3. **Modelo realista no dashboard**: se o modelo realista vira o principal, o dashboard deve usar ele. Decisão final do orientador.
4. **Reclassificação de risco**: se a persistência supera o classificador, a Tabela 13 precisa de uma coluna "regressão + limiares" como método recomendado. Verificar se script 56 já tem isso (os alertas_por_limiar são exatamente isso).
