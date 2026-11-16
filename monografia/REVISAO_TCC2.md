# Revisão da monografia do TCC 2

| | |
|---|---|
| **Revisão 1** | 10/11/2026, sobre a `main` em `aa98c9c` (antes da v4 corrigida) |
| **Revisão 2** | 15/11/2026, sobre a `main` em `0ad0b40` (PR #3 do Pedro) + PR #4 do Thiago (`docs/texto-thiago`) |
| **Dados de referência** | MODELO-PREVISAO `a608385` (v4 com o INMET corrigido) + script 57 (PR #3 do MODELO-PREVISAO) |

Os números de linha se referem aos arquivos em `monografia/editaveis/` na branch `docs/texto-thiago`.

## Resumo do status

- **A v4 foi refeita com o INMET corrigido** (Pedro, MODELO-PREVISAO `a608385`): 27 anos completos, nenhum ano sem Silver, cobertura de 87–93% em 2009, 2020 e 2022.
- **A maior parte da revisão 1 foi concluída** (PRs #3 e #4 do TCC2-DOCS). Restam três blocos:
  1. **Capítulo 4 misturado:** seções da v3 convivem com as da v4 (base de modelagem, tabela antes/depois, SHAP, classificação). É o principal pendente.
  2. **Análises que dependem do treino da v4:** cegueira de dados e alertas por limiar. Estão bloqueadas pelo acesso do Thiago ao dataset restrito no HuggingFace.
  3. **Números da v4 desatualizados em seções do Pedro:** classificação e Optuna, que vieram da rodada anterior à correção do INMET.
- **Os marcadores `[PENDENTE: ...]` no texto** indicam onde ainda falta resultado. Todos precisam sumir antes da entrega.

## Decisões do orientador (mantidas)

- Manter o treino da **v4**; mais testes de hiperparâmetros ficam para trabalhos futuros.
- Foco em prever o **momento** do surto, não o número absoluto, com bibliografia sobre a dificuldade de prever a magnitude dos picos.
- **Mesorregiões** no lugar de municípios, com a justificativa da agregação.
- Justificar com bibliografia o efeito pequeno do clima e o INMET como alternativa ao SINAN.
- Explicar o que cada hiperparâmetro faz.

## Decisão da equipe (15/11/2026)

Os números da monografia vêm da rodada do Pedro (snapshot do SINAN usado em `a608385`). Uma reprodução com um snapshot mais recente mostrou que **as semanas finais de 2026 desse snapshot estavam incompletas** por atraso de notificação. Isso explica o R²_log baixo de 2026 (≈0,57) e puxa o agregado para baixo; 2024 e 2025 batem entre os dois snapshots. O texto já registra essa limitação. Atualizar o snapshot fica como opção futura.

---

## 1. Concluído

### Itens da revisão 1

| Item | Onde foi resolvido |
|---|---|
| Título com "Mesorregiões" | PR #3 (Pedro) |
| Metodologia descrevendo a v4 (janelas × atributos, 9 combinações, curva de aprendizado, Optuna, PSI) | PR #3 (Pedro) |
| Limitações "treino de quatro anos" e "hiperparâmetros fixos" atualizadas | PR #3 (Pedro) |
| Capítulo de sistema (dashboard v4, GitHub Actions, HuggingFace, Kaggle; API como legado) | PR #3 (Pedro) |
| Cronograma até novembro de 2026 | PR #3 (Pedro) |
| Introdução enxugada (parte clínica, números sem fonte, analogia da umidade) — itens 7 e 8 | PR #3 (Pedro) |
| Seções repetidas do referencial fundidas (clima e dengue no Brasil; defasagens) | PR #3 (Pedro) |
| Item 4: "objetivo" de defasagens ótimas removido | PR #3 (Pedro) |
| Item 10: contagem da semana *t* (nota do `recorte.json` corrigida; não entra como atributo) | MODELO-PREVISAO `a608385` (Pedro) |
| Item 1: DF 313 mil × 256 mil — na base do trabalho são 277 mil notificações de residentes em 2024; o teste soma 255 mil porque o alvo é *t*+4 | PR #4 (Thiago) |
| Item 2: número único para 2024 (6,6 milhões de notificações) e diferença entre notificações e casos prováveis | PR #4 (Thiago) |
| Item 3: dados globais e parte clínica citando a OMS (2025) no lugar de `naish2014climate` | PR #4 (Thiago) |
| Item 5: temperaturas padronizadas no referencial | PR #4 (Thiago) |
| Item 9: frase incompleta da tabela comparativa | PR #4 (Thiago) |
| Pergunta de pesquisa e objetivos com foco no momento do surto | PR #3 (Pedro) e PR #4 (Thiago) |
| Resumo e abstract só com números da v4 e foco no momento | PR #4 (Thiago) |

### Tarefas novas da divisão

| Tarefa | Onde |
|---|---|
| Referencial: "Previsibilidade do Momento e da Magnitude dos Surtos" (Johansson et al. 2019; Reich et al. 2016) | PR #4 (Thiago) |
| Referencial: "O Papel do Clima na Previsão de Curto Prazo" (Johansson et al. 2016; Reich et al. 2016; Lowe et al. 2016) | PR #4 (Thiago) |
| Referencial: "Concept Drift em Séries Epidemiológicas Longas" | PR #3 (Pedro) |
| Metodologia: escolha da escala espacial (distância até a estação, municípios por estação, tamanho da base) | PR #4 (Thiago) |
| Metodologia: tabela de hiperparâmetros com a função de cada um | PR #4 (Thiago) |
| Metodologia: métricas de momento (erro na semana do pico, acerto de direção) | PR #4 (Thiago) |
| Baselines no teste da v4 e desempenho por ano (script 57, com os modelos salvos, sem retreino) | PR #4 (Thiago) + MODELO-PREVISAO PR #3 |
| Resultados: seção "Antecipação do Momento dos Surtos" | PR #4 (Thiago) |
| Resultados: contribuição do clima na v4 (23/27 UFs, 99/137 mesorregiões, walk-forward 0,809 × 0,803) | PR #4 (Thiago) |
| Resultados: recorte do DF na v4 (tabela própria) | PR #4 (Thiago) |
| Resultados v4: 9 combinações, curva de aprendizado, PSI, Optuna, walk-forward expandido, classificação, SHAP | PR #3 (Pedro) — ver pendências dos números |
| Síntese e conclusão com números da v4 | PR #4 (Thiago), exceto os trechos marcados `[PENDENTE]` |
| `gerar_figuras.py` e as duas figuras de baselines e série nacional na v4 | PR #4 (Thiago) |
| `RASTREABILIDADE.md` apontando para `a608385`, com nomes de scripts corrigidos | PR #4 (Thiago) |
| Notebooks do Kaggle com os hiperparâmetros do pipeline | MODELO-PREVISAO `2542185` (Pedro) |

---

## 2. Pendente

Prioridade: **A** = bloqueia a entrega ou gera inconsistência visível; **B** = importante; **C** = acabamento.

### Pedro

| # | Prioridade | Onde | O que fazer |
|---|---|---|---|
| P1 | A | `resultados.tex:4` | Abertura do capítulo: teste com **16.029** linhas (não 16.988); incluir a seção de momento na lista de seções. |
| P2 | A | `resultados.tex:6-40` | "Base de modelagem" é da v3 (60.554 linhas, 2018–2026, cobertura 90,1%, figura de cobertura v3). Na v4: 188.512 linhas, 2000–2026, cobertura de 72,1% (`42_integration_report.json`); usar `fig_v4_inmet_coverage.png`. A tabela antes/depois e o parágrafo da linha 19 usam "modelo A/C" com o sentido da v3: rotular explicitamente como v3 (efeito das correções) ou refazer. |
| P3 | A | `resultados.tex:376-408`, `tabelas/tab_v4_classification.tex` | Classificação v4 com números da rodada anterior à correção do INMET. Relatório 54 atual: A enriquecido **0,501** (AUC 0,780), B **0,585** (0,835), C **0,583** (0,836); ganho da série longa **+0,084** (não +0,094). O resumo e a conclusão já usam 0,50 → 0,59. |
| P4 | A | `resultados.tex:228-250` | Classificação da v3 (persistência 0,622, "XGBoost A/B/C" no sentido de atributos) duplicada com a seção v4. Fundir numa só seção da v4. |
| P5 | A | `resultados.tex:191-226` e `410-422` | SHAP aparece duas vezes. A figura `fig_v3_shap_beeswarm` e a tabela de limiares (temperatura média 21 °C, precipitação 0,11 mm/h etc.) são da v3. Na v4, a primeira variável climática continua sendo a temperatura mínima (20.ª), mas a segunda passa a ser a umidade (média de 4–8 semanas, 22.ª). Refazer os limiares na v4 — dá para fazer com os modelos salvos, sem retreino — e fundir as duas seções. |
| P6 | B | `resultados.tex` (Optuna), `49_optuna_report.json` | O Optuna ainda é da rodada de 04/11, antes da correção do INMET. Rodar de novo ou avisar no texto. |
| P7 | B | `metodologia.tex:25, 57, 59, 127` | Tabela de etapas cita "três variantes" e *data blindness*; conferência com a Gold de "2018 a 2026" (é 2000–2026); cobertura de 90,1% (v4: 72,1%); proporções de classes 52,9% / 12,1% (v4, treino B: 51,9% / 9,8%). |
| P8 | B | HuggingFace | Aprovar o acesso do Thiago ao dataset `dengue-tcc2-data` (desbloqueia T1 e T2). |
| P9 | B | GitHub | Revisar e fazer o merge de MODELO-PREVISAO PR #3 (script 57) e TCC2-DOCS PR #4. |
| P10 | C | `tabelas/`, `figuras/resultados_v4/` | Seis tabelas geradas e quatro figuras (`gain_comparison`, `r2_by_year`, `inmet_coverage`, `confusion_matrix`) não são usadas no texto. Usar ou remover. |
| P11 | C | `bibliografia.bib` | Conferir `yurdakul2020statistical` (autores e número da revista parecem incompletos). |
| P12 | C | Kaggle | Confirmar que o notebook de treino usa o baseline sazonal "mesma semana do ano anterior" e que o resumo não diz que o XGBoost vence em todas as escalas. |

### Thiago

| # | Prioridade | Onde | O que fazer |
|---|---|---|---|
| T1 | A | `resultados.tex:160-190`, síntese, conclusão | Cegueira de dados na v4 (script 56, já pronto): substituir a tabela e a figura da v3 e remover os três `[PENDENTE]`. Depende do P8. Numa reprodução com outro snapshot, o resultado estranho da v3 (atraso de 4 semanas acima do completo) não se repetiu. |
| T2 | A | `conclusao.tex:12` | Alertas por limiar na v4 (regressão × persistência × classificador, script 56). Depende do P8. Numa reprodução com outro snapshot, os alertas derivados da regressão superaram a persistência (F1 0,72 × 0,66), o que inverteria a conclusão da v3. |
| T3 | B | `informacoes.tex:18-20` | Data da defesa e banca. |
| T4 | C | Fechamento | Depois dos merges: atualizar `RASTREABILIDADE.md` (commit de merge), rodar `gerar_figuras.py`, compilar e conferir que não restou nenhum `[PENDENTE]`. |

### Juntos

| # | Prioridade | O que fazer |
|---|---|---|
| J1 | B | Revisão final de repetições (seção 3) depois que o capítulo 4 estiver só com a v4. |
| J2 | C | Revisão de português e de formatação do PDF final (inclusive duas caixas largas demais: o `\texttt` da seção SHAP v4 e a URL do capítulo de sistema). |

---

## 3. Repetições que ainda restam

| Assunto | Onde | Sugestão |
|---|---|---|
| SHAP | `resultados.tex` "Interpretação do Modelo" e "SHAP v4" | Uma seção só (P5). |
| Classificação | `resultados.tex` "Classificação do Nível de Risco" (v3) e "Classificação em Quatro Faixas de Risco (v4)" | Uma seção só (P4). |
| Walk-forward | Clima (texto) e "Walk-Forward Expandido (v4)" | Já resolvido no texto do clima, que remete à seção v4; manter assim. |
| Erro de mapeamento do INMET | Resumo, abstract, introdução, objetivos, contribuições, metodologia (tabela e parágrafo), resultados (tabela antes/depois), conclusão | Detalhar só na metodologia; nos demais, uma frase. |
| Árvores não extrapolam e treino em log | Referencial (`sec:xgboost` e considerações finais), resultados, conclusão | Explicar no referencial e só retomar nos resultados. |
| Cegueira de dados "otimista" | Metodologia, resultados, conclusão | Manter na metodologia e nas limitações. |

---

## 4. Divisão das tarefas restantes

**Pedro:** P1 a P12, ou seja, o capítulo 4 só com a v4, a classificação, o SHAP, o Optuna, os detalhes da metodologia, o acesso ao HuggingFace e os merges.

**Thiago:** T1 a T4 — cegueira de dados e alertas na v4 (assim que o acesso for aprovado), banca e fechamento.

**Regras:**
- Os números do texto saem sempre de relatórios versionados no MODELO-PREVISAO (scripts 40–57), nunca do Kaggle.
- Qualquer número novo entra também no `RASTREABILIDADE.md`.
- Nada de `[PENDENTE]` no PDF entregue ao orientador.
