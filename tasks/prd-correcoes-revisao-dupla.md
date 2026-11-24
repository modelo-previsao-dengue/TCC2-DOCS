# PRD: Correções Técnicas — Revisão da Dupla (Thiago)

## Introdução

O Thiago revisou o PR #5 e os scripts 58–61 e levantou 6 pontos técnicos com impacto nos números reportados na monografia. Este PRD cobre as correções nos scripts, a re-execução dos relatórios e a atualização da monografia com os números corrigidos.

**Prazo:** 27/nov/2026 (entrega ao orientador).
**Divisão:** Pedro corrige scripts e atualiza números na monografia; Thiago cuida de texto, forma, pergunta de pesquisa e cronograma.

## Diagnóstico dos 6 Pontos

| # | Ponto do Thiago | Verificação contra o código | Veredito |
|---|---|---|---|
| 1 | MASE usa média do treino, não persistência | `script 60:102-111` — denominador é `train_means.get(meso)`, não `notificacoes_t` | **VÁLIDO** — claim "vence persistência em 137" não se sustenta com esse denominador |
| 2 | Ridge sem log nem padronização, CV embaralhado | `script 59:115` — target JÁ está em `log1p` (Thiago errou neste ponto). Features sem `StandardScaler` e `RidgeCV(cv=5)` embaralhado | **PARCIAL** — target ok; falta log1p nas features de contagem + scaler + CV temporal |
| 3 | Δ vazamento = 0.0005 confunde com adição de `notificacoes_t` | Report 58: completo=0.8891, realista=0.8886, realista_sem_notif_t=0.8861 | **VÁLIDO** — Δ puro (completo vs realista_sem_notif_t) = 0.003, não 0.0005 |
| 4 | Antecedência: modelo=6sem, tendência=7sem, não é ganho | Report 61: modelo mediana=6.0, tendência mediana=7.0 | **VÁLIDO** — tendência observada alerta 1 semana antes do modelo |
| 5 | DM/bootstrap só compara modelo vs persistência, falta clima×sem_clima | `script 60` só roda DM(modelo, persistência); nenhum teste formal clima vs sem_clima | **VÁLIDO** — falta teste que era pedido do Fabiano |
| 6 | Cenários de atraso (script 56) usam features com vazamento | `script 56:78-80` usa `feature_sets()` do schema completo (266 features) | **VÁLIDO** — `qt_confirmados_provaveis` e demais delayed presentes |

**Achado adicional da auditoria do PRD:** a monografia ainda contém p-values inflados de testes $t$ pareados ($p < 10^{-46}$, $p < 10^{-30}$, $p < 10^{-300}$, etc.) em `resultados.tex` linhas 131, 150, 159–162, 220. O Thiago pediu explicitamente para tirá-los. A linha 243 já reconhece que são inflados, mas as tabelas e parágrafos anteriores ainda os usam.

## Objetivos

- Corrigir o cálculo do MASE para usar persistência como denominador
- Corrigir o Ridge com log1p nas features, StandardScaler e alpha escolhido no val set temporal
- Reportar Δ de vazamento correto (completo vs realista_sem_notif_t = 0.003)
- Corrigir framing da antecedência (modelo 6 sem vs tendência 7 sem — sem vender como ganho)
- Adicionar teste DM + bootstrap para clima vs sem_clima (pedido do Fabiano)
- Refazer cenários de atraso com features realistas
- Remover p-values inflados dos testes $t$ pareados
- Atualizar monografia com todos os números corrigidos
- Validar consistência entre relatórios JSON e texto

## User Stories

### Fase 1 — Correções sem Retreino (edição de relatório/texto)

#### US-001: Corrigir Δ de vazamento temporal no relatório
**Descrição:** Como pesquisador, quero reportar o delta correto de vazamento (completo vs realista_sem_notif_t), porque o Δ=0.0005 confunde remoção de 61 features com adição de `notificacoes`.

**Acceptance Criteria:**
- [ ] No `58_vazamento_temporal_report.json`: campo `comparacao` passa a ter `delta_puro` = 0.003 (completo 0.8891 vs realista_sem_notif_t 0.8861) como métrica principal
- [ ] Manter `delta_com_notificacoes` = 0.0005 como informação secundária com nota explicativa
- [ ] **Não precisa re-rodar** o script 58 — os 3 cenários já estão no relatório

#### US-002: Corrigir framing da antecedência no relatório
**Descrição:** Como pesquisador, quero que o relatório de antecedência não apresente as 6 semanas do modelo como ganho, já que a tendência observada detecta a subida em 7 semanas (melhor).

**Acceptance Criteria:**
- [ ] No `61_classificacao_completa_report.json`: adicionar campo `interpretacao`: "tendência observada (mediana 7 sem) detecta a subida antes do modelo (mediana 6 sem); a antecedência do modelo NÃO é superior à da tendência observada"
- [ ] **Não precisa re-rodar** o script 61

### Fase 2 — Correções com Retreino

#### US-003: Corrigir MASE para usar persistência como denominador
**Descrição:** Como pesquisador, quero que o MASE meça o erro do modelo relativo à persistência (MAE_modelo / MAE_persistência por mesorregião), para que a comparação "modelo vs persistência" seja direta.

**Acceptance Criteria:**
- [ ] No `script 60`, função `mase_per_mesoregion`: adicionar variante onde denominador é `MAE_persistência` por mesorregião, usando `notificacoes` semana t como previsão naive
- [ ] Fórmula: `MASE_pers[meso] = mean(|y - pred_modelo|) / mean(|y - notificacoes_t|)` para cada mesorregião
- [ ] Manter MASE original (denominador = média do treino) renomeado como `MASE_media`
- [ ] Reportar: mediana, p25, p75, % abaixo de 1, lista das mesorregiões com MASE_pers ≥ 1 (se houver)
- [ ] Relatório `60_metricas_corrigidas_report.json` atualizado com seção `mase_vs_persistencia`
- [ ] Re-rodar script 60 e verificar que outros números (DM, bootstrap) não mudaram

#### US-004: Corrigir Ridge com log1p + StandardScaler + CV temporal
**Descrição:** Como pesquisador, quero que o baseline Ridge use log1p nas features de contagem, StandardScaler e alpha escolhido na validação temporal, para que o R²_log do Ridge seja correto.

**Acceptance Criteria:**
- [ ] No `script 59`, função `ridge_ar`:
  - Aplicar `np.log1p` nas features de contagem (notificacoes, lags, médias móveis, diffs — prefixo `notificacoes_`) antes de escalar
  - Adicionar `StandardScaler()` fitado no treino, transformando treino/val/teste
  - Trocar `RidgeCV(cv=5)` por loop manual: fit Ridge com cada alpha em [0.01, 0.1, 1, 10, 100] no treino, avaliar R²_log no val, escolher o melhor alpha
- [ ] Reportar alpha escolhido, R²_log no val, e R²_log/R²/MAE/RMSE no teste
- [ ] Relatório `59_baselines_avancados_report.json` atualizado
- [ ] Re-rodar script 59 completo (climatologia e controles não mudam, mas regenerar para consistência)

#### US-005: Adicionar DM + bootstrap para clima vs sem_clima
**Descrição:** Como pesquisador, quero um teste estatístico formal comparando modelo com clima vs modelo sem clima, que era o pedido original do Fabiano e que o Thiago cobrou.

**Acceptance Criteria:**
- [ ] Criar script `62_dm_clima.py` com:
  - Treinar modelo realista **com_clima** (203 features, inclui INMET) — pode reaproveitar do script 60
  - Treinar modelo realista **sem_clima**: features realistas menos TODAS as INMET (remover features com prefixo `rain_`, `temp_`, `humidity_`, `pressure_`, `wind_`, `radiation_`)
  - Reportar R²_log de cada um no teste e por ano
- [ ] Diebold-Mariano ponto-a-ponto (escala log, h=4) entre com_clima vs sem_clima
- [ ] Diebold-Mariano sobre a **perda média semanal entre regiões**: para cada semana epidemiológica no teste, calcular `mean_across_meso(loss_com - loss_sem)`, depois rodar DM sobre essa série temporal agregada (elimina correlação espacial)
- [ ] Bootstrap em blocos (mesorregião×ano, 5000 iter) para IC do Δ R²_log
- [ ] Relatório `62_dm_clima_report.json` com DM stats, p-values e IC
- [ ] Se p > 0.05 no DM agregado: documentar que o ganho não atinge significância estatística formal no nível 5%

#### US-006: Refazer cenários de atraso com features realistas
**Descrição:** Como pesquisador, quero que os cenários de atraso (blindness) usem o conjunto realista (203 features), porque o script 56 atual inclui features com vazamento temporal (ex: `qt_confirmados_provaveis`).

**Acceptance Criteria:**
- [ ] Criar script `63_atraso_realista.py`:
  - Base = `get_realista_features()` (203 features, sem delayed)
  - Cenário **completo realista**: todas as 203
  - Cenário **atraso 4w**: remove `notificacoes_lag_1w` a `_4w`, `notificacoes_diff_1w`, `notificacoes_pct_change_1w`, `notificacoes_media_movel_2_4w`
  - Cenário **atraso 8w**: atraso 4w + remove `_lag_5w` a `_8w`, `notificacoes_media_movel_4_8w`
  - Cenário **só clima**: apenas features INMET + codificação cíclica da semana (`week_of_year_sin`, `week_of_year_cos`)
  - Para cada cenário: com_clima e sem_clima
- [ ] Treinar com splits_b (treino, val, teste), mesmos XGB_PARAMS
- [ ] Reportar R²_log, R², MAE, RMSE por cenário + Δ entre com e sem clima
- [ ] **Não reportar p-values de t-test pareado** — usar apenas Δ e IC bootstrap se necessário
- [ ] Relatório `63_atraso_realista_report.json`

### Fase 3 — Atualização da Monografia

#### US-007: Remover p-values inflados de t-tests pareados
**Descrição:** Como pesquisador, quero remover todos os p-values de testes $t$ pareados que estão inflados pela autocorrelação, substituindo por referência ao DM/bootstrap já calculados.

**Acceptance Criteria:**
- [ ] `resultados.tex:131` — remover `$p<10^{-30}$`; manter só "consistente" ou referenciar DM clima (US-005)
- [ ] `resultados.tex:150` — remover `$p < 10^{-21}$` e `$p < 10^{-17}$` dos cenários de atraso; usar apenas Δ
- [ ] `resultados.tex:159-162` — tabela `tab:blindness`: remover coluna de p-value inteira (ou substituir pela coluna Δ já existente); atualizar números com US-006
- [ ] `resultados.tex:220` — remover `$p < 10^{-46}$` do teste série longa vs curta; manter Δ=+0,015
- [ ] Verificar que a linha 243 (que já reconhece a inflação) ainda faz sentido após as remoções
- [ ] Nenhum `$p < 10^{-` restante no texto que venha de t-test pareado

#### US-008: Atualizar resultados.tex com números corrigidos
**Descrição:** Como pesquisador, quero que a seção de resultados reflita todos os números corrigidos dos scripts.

**Acceptance Criteria:**
- [ ] **MASE** (4 ocorrências):
  - Linha 30: atualizar mediana e "abaixo de 1 em todas as 137" → ajustar conforme US-003
  - Linha 369 (síntese item 1): idem
- [ ] **Vazamento Δ** (2 ocorrências):
  - Linha 26: trocar "Δ=0,0005" por "Δ=0,003" com nota sobre `notificacoes`
  - Linha 369 (se mencionar): idem
- [ ] **Antecedência**:
  - Parágrafo do momento (~linha 325): reportar modelo=6sem E tendência=7sem, nota de que tendência detecta antes
  - Linha 369 (síntese item 1): ajustar framing
- [ ] **Ridge** (se R² mudou com US-004):
  - Linha 28: atualizar R²_log do Ridge
  - Tabela `tab:baselines`: atualizar linha do Ridge
- [ ] **Clima** (se DM disponível de US-005):
  - Parágrafo ~linha 131: substituir p-values do t-test por resultado do DM/bootstrap clima vs sem_clima
  - Síntese item 3 (linha 371): atualizar com resultado formal
- [ ] **Blindness** (US-006):
  - Tabela `tab:blindness` (linhas 155-163): substituir números inteiros com resultados realistas
  - Parágrafo (linha 150): atualizar texto correspondente
- [ ] **Síntese** (linhas 367-377): verificar TODOS os 5 itens contra números novos

#### US-009: Atualizar conclusao.tex e resumo.tex
**Descrição:** Como pesquisador, quero que conclusão e resumo reflitam os números corrigidos.

**Acceptance Criteria:**
- [ ] **conclusao.tex:8** — "Respostas à Pergunta de Pesquisa":
  - MASE: ajustar "137 mesorregiões" conforme US-003
  - Antecedência: "mediana de 6~semanas" → reportar modelo vs tendência
- [ ] **conclusao.tex:23** — Limitação vazamento: trocar Δ=0,0005 por Δ=0,003
- [ ] **conclusao.tex:10** — Clima: se DM não significativo, ajustar tom
- [ ] **resumo.tex:2** — Atualizar:
  - "queda de apenas 0,0005" → "queda de 0,003"
  - "todas as 137 mesorregiões" → ajustar conforme MASE
  - "mediana de 6~semanas de antecipação" → modelo 6 / tendência 7
  - Ridge R²_log se mudou
- [ ] Compilar LaTeX sem erros (`latexmk -pdf`)
- [ ] Nenhum `$p < 10^{-` restante de t-test pareado em nenhum dos 3 arquivos

### Fase 4 — Validação e Entrega

#### US-010: Validação cruzada números × texto
**Descrição:** Como pesquisador, quero verificar que nenhum número na monografia contradiz os relatórios JSON, antes de entregar ao orientador.

**Acceptance Criteria:**
- [ ] Script de validação (ou checklist manual) que extrai números-chave dos relatórios JSON e compara com o texto:
  - R²_log do modelo realista
  - R²_log da persistência
  - MASE mediana e % abaixo de 1
  - Δ vazamento
  - DM stat e p-value (modelo vs persistência)
  - DM stat e p-value (clima vs sem_clima) — se disponível
  - Ridge R²_log
  - F1 macro classificação
  - Antecedência modelo e tendência
- [ ] Zero inconsistências encontradas
- [ ] Commit e push sem vestígio de IA
- [ ] PR aberto (ou merge no feat/monografia existente)

## Requisitos Funcionais

- FR-1: `MASE_pers = MAE_modelo / MAE_persistencia` por mesorregião, onde `MAE_persistencia = mean(|y_true - notificacoes_t|)`
- FR-2: Ridge deve aplicar `np.log1p` nas features de contagem antes de `StandardScaler().fit(X_train)`
- FR-3: Alpha do Ridge deve ser escolhido maximizando R²_log no val set temporal, não em CV embaralhado
- FR-4: O Δ de vazamento reportado como principal deve ser completo (0.8891) vs realista_sem_notif_t (0.8861) = 0.003
- FR-5: DM clima vs sem_clima ponto-a-ponto deve usar h=4 e correção Newey-West (mesma implementação do script 60)
- FR-6: DM agregado semanal: `d_t = mean_meso(loss_com_t - loss_sem_t)` para cada semana t, depois DM sobre a série `{d_t}`
- FR-7: "sem_clima" = features realistas (203) menos todas com prefixo `rain_`, `temp_`, `humidity_`, `pressure_`, `wind_`, `radiation_`
- FR-8: Cenários de atraso devem partir de `get_realista_features()` e remover lags adicionais
- FR-9: Nenhum p-value de teste $t$ pareado deve permanecer no texto final
- FR-10: Todos os relatórios JSON devem ser re-gerados com os números atualizados
- FR-11: LaTeX deve compilar sem erros após todas as edições

## Fora de Escopo

- Não mudar a arquitetura do modelo (XGBoost, hiperparâmetros, splits)
- Não refazer SHAP (os top 10 do modelo realista já estão corretos)
- Não mexer na classificação (F1 não é afetado por essas correções)
- Não mexer na curva de aprendizado ou PSI
- Não mexer no controle região+semana (R²_log=0.276) — já está correto
- Texto de forma, formatação LaTeX, cronograma, pergunta de pesquisa — fica com o Thiago
- Não criar novos baselines além dos já existentes

## Considerações Técnicas

- **Scripts a modificar:** 59 (Ridge), 60 (MASE)
- **Scripts a criar:** 62 (DM clima), 63 (atraso realista)
- **Relatórios a editar (sem re-rodar):** 58 (vazamento Δ), 61 (antecedência framing)
- **Monografia:** resultados.tex, conclusao.tex, resumo.tex
- **Tempo de compute estimado:** ~15-20 min por script com treino XGBoost
- **Dependências:**
  - Fase 1 (US-001, US-002): sem dependência, pode executar imediatamente
  - Fase 2 (US-003 a US-006): independentes entre si, podem rodar em paralelo
  - Fase 3 (US-007 a US-009): depende de TODOS os números da Fase 2
  - Fase 4 (US-010): depende de Fase 3
- **Risco principal:** se MASE_persistência ≥ 1 em várias mesorregiões, a frase-chave da monografia muda significativamente. Mitigação: reportar mediana e % abaixo de 1 em vez de "todas".
- **Risco secundário:** se DM clima der p > 0.05, o argumento "clima significativo" enfraquece. Mitigação: o IC bootstrap e a consistência entre UFs/mesorregiões ainda sustentam o argumento de que o ganho é real, mesmo que pequeno demais para significância no DM.

## Métricas de Sucesso

- Todos os 6 pontos do Thiago resolvidos ou respondidos com justificativa técnica
- Nenhum p-value de t-test pareado restante no texto
- Nenhum número na monografia contradiz os relatórios JSON
- LaTeX compila sem erros
- Commit e push sem vestígio de IA
- Entrega ao orientador até 27/nov

## Questões em Aberto

1. **MASE com persistência ≥ 1 em algumas mesorregiões:** qual framing usar? Proposta: "mediana 0,XX, abaixo de 1 em NN das 137 mesorregiões (XX%)" — reportar honestamente.
2. **DM clima não significativo:** como reportar o ganho do clima? Proposta: manter IC bootstrap como evidência de ganho consistente, declarar que o DM formal não rejeita a nula ao nível 5%, e discutir que o tamanho do efeito (+0,008) pode ser clinicamente relevante mesmo sem significância estatística.
3. **Ridge corrigido sobe muito:** se o R²_log do Ridge subir de 0.456 para, digamos, 0.60+, o gap para o XGBoost (0.889) diminui mas continua grande. Reportar honestamente.
4. **Antecedência — vale manter no texto?** O modelo (6 sem) é pior que a tendência observada (7 sem). Proposta: manter como resultado descritivo ("o modelo antecipa a subida, mas não mais cedo que a tendência observada nos dados"), e discutir na limitação que a tendência observada não está disponível em tempo real.
