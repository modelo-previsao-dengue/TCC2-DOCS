# Revisão da monografia do TCC 2

Revisão completa do texto em LaTeX (`monografia/`), feita em 10/11/2026 sobre a `main`
(merge do PR #1, commit `aa98c9c`). O objetivo é listar o que está **desatualizado**,
**inconsistente** ou **repetitivo** antes da rodada de ajustes, e dividir o trabalho
entre Thiago e Pedro.

Os números de linha se referem aos arquivos em `monografia/editaveis/`.

## Decisões do orientador que guiam a revisão

- Manter o treino da **v4**; mais testes de hiperparâmetros ficam para trabalhos futuros.
- Não enfatizar a previsão do **número absoluto** de casos: o foco é prever o **momento** do surto,
  com bibliografia explicando por que a magnitude de picos históricos é difícil de prever.
- Trocar "municípios" por **mesorregiões** e justificar a agregação (granularidades diferentes
  das duas bases e escolhas técnicas).
- Justificar com bibliografia por que o clima teve menos impacto do que o esperado e mostrar o
  valor do INMET como alternativa quando faltam dados do SINAN.
- Explicar o que cada hiperparâmetro faz.

## 1. Desatualizado

### Em relação às decisões do orientador e à v4

| Onde | Problema | Responsável |
|---|---|---|
| `informacoes.tex:6` | O título ainda diz "Municípios"; o texto todo é sobre mesorregiões. | Thiago |
| `informacoes.tex:18-21` | Data da defesa e banca ainda com os textos de exemplo do template. | Thiago |
| `metodologia.tex:4, 80-94` | Tudo descreve a v3: `rodar_v3.sh`, treino 2019–2022, 60.554 linhas e a tabela de divisão temporal. A v4 treina de 2001 a 2022, com aquecimento em 2000. | Pedro |
| `metodologia.tex:120-126` e capítulo de resultados | Conflito de nomes A/B/C. No texto, A/B/C são conjuntos de atributos; na v4, são janelas de treino. Trocar por nomes descritivos, como "só SINAN / INMET bruto / INMET enriquecido" e "janela curta / série longa / série longa ponderada". | Pedro |
| Resumo, abstract, `introducao.tex:118, 127` | A pergunta de pesquisa e o objetivo geral falam em prever o número de notificações; o foco agora é o momento do surto. Os números do resumo (R² 0,87, "cerca de metade", 39%) são da v3. | Thiago |
| `conclusao.tex:21` | A limitação "o treino cobre quatro anos" deixa de valer com a série longa da v4. | Pedro |
| `conclusao.tex:26` | A limitação "hiperparâmetros fixos" ignora que o Optuna foi testado na v4 e não foi adotado. | Pedro |
| `metodologia.tex:51`, `resultados.tex:9` | A cobertura climática de 90,1% é da v3; com a série desde 2000 ela muda, porque a rede de estações era menor nos primeiros anos. | Pedro |
| `sistema.tex` (capítulo inteiro) | Diz que a API e o Streamlit usam o modelo municipal antigo e que o painel é anterior ao reprocessamento. Hoje existem o dashboard da v4, o fluxo semanal e a sincronização com o HuggingFace. Revisar também a tabela de endpoints (`/predict/{municipio}`). | Pedro |
| `cronograma.tex:20, 35` | Diz que a execução foi "até setembro de 2026"; faltam outubro e novembro (v4, dashboard, HuggingFace, Kaggle e revisão da monografia). | Pedro |
| `conclusao.tex:27, 38` | "Sistemas desatualizados" e "automatizar a atualização semanal" aparecem como limitação e trabalho futuro, mas já foram feitos. | Pedro |

### Experimentos da v4 sem nenhuma menção no texto

Série longa, peso de recência, curva de aprendizado, *drift* (PSI), Optuna e a nova
classificação de risco. Responsável: **Pedro** (metodologia e resultados da v4).

### Dependência: v4 com o INMET corrigido

Os dados climáticos da v4 (no repositório, no HuggingFace e nos notebooks do Kaggle) ainda
foram gerados com o extrator antigo: a "umidade" é o ponto de orvalho, as temperaturas mínima
e máxima estão trocadas, o "vento" é a rajada, e faltam 2009, 2020 e 2022 (cobertura de cerca
de 65%). Os resultados **só com SINAN** são confiáveis; os que usam **clima** precisam ser
refeitos depois de reprocessar o INMET com o código corrigido e rodar a v4 de novo. As seções
que dependem disso estão marcadas com ⏳ na divisão abaixo.

## 2. Inconsistências

| # | Onde | Problema | Responsável |
|---|---|---|---|
| 1 | `introducao.tex:14` × `resultados.tex:241` | O DF teria **313.317 casos em 2024**, mas a seção do DF diz **256 mil notificações em todo o teste** (2024–2026). Os dois não podem estar certos, a menos que meçam coisas diferentes (município de notificação × residência, casos × notificações). Explicar ou corrigir. | Thiago |
| 2 | `introducao.tex:10`, `referencial_teorico.tex:8`, resumo, `metodologia.tex:96`, `resultados.tex:78` | A magnitude de 2024 aparece de quatro formas: "6 milhões de casos prováveis no 1.º semestre", "mais de 6 milhões de casos prováveis", "cerca de 6,5 milhões de notificações" e 6,44 milhões. Escolher um termo (notificações ou casos prováveis) e explicar a diferença uma vez. | Thiago |
| 3 | `introducao.tex:8` | Os dados de 2019 (5,2 milhões de casos) são atribuídos a `naish2014climate`, um artigo de 2014. Trocar a fonte (ex.: OMS). | Thiago |
| 4 | `referencial_teorico.tex:20` | Diz que identificar as defasagens ótimas é "um dos objetivos específicos deste trabalho", mas esse objetivo não está na lista (`introducao.tex:131-143`). Sobra do TCC 1. | Thiago |
| 5 | `introducao.tex:43`, `referencial_teorico.tex:16, 20, 102` | A incubação no ser humano aparece como "4 a 10 dias" e "4 a 7 dias". No mesmo parágrafo, a temperatura ótima é "25 a 30 °C" e o pico de transmissão é "perto de 24 °C". Padronizar com fonte. | Thiago |
| 6 | `resultados.tex:160-161` | Na cegueira de dados, o cenário com atraso de 4 semanas sem clima (R² log 0,868) fica **acima** do cenário completo (0,859): remover informação melhorou o modelo. O texto não explica. Investigar (variação entre treinos, efeito de regularização) e comentar. | Thiago |
| 7 | `introducao.tex:65, 73, 77, 81, 85, 89` | Números concretos sem citação: "até 40% com sintomas persistentes", "ocupação acima de 95%", "dezenas de óbitos", "estudos econômicos estimam", "R$ 500 a R$ 2.000 por caso", "R$ 5 bilhões", taxas maiores em regiões de IDH baixo. Citar ou remover. | Thiago |
| 8 | `introducao.tex:97-99` | A analogia diz que o modelo alerta "antes que os casos clínicos comecem a aparecer" e usa umidade acima de 70% como exemplo. Os resultados mostram que o modelo depende principalmente da série de casos, e a "umidade" era justamente o erro de dados. | Thiago |
| 9 | `referencial_teorico.tex:76` | Frase incompleta: "Baseado em características gerais e estudos comparativos típicos..." termina sem verbo principal e sem ponto. | Thiago |
| 10 | `metodologia.tex:103` × `config/recorte.json` | O texto diz que a contagem da semana *t* não é atributo, o que bate com o `feature_schema` da v3 e da v4. Mas a configuração tem `"incluir_notificacoes_atual": true`, com nota dizendo que ela passou a ser incluída. Confirmar qual vale, porque isso também explica por que a persistência vence. | Pedro |

## 3. Repetições

| Assunto | Vezes | Onde | Sugestão |
|---|---|---|---|
| Erro de mapeamento do INMET e a "umidade de 15,7" | cerca de 8 | Resumo, abstract, introdução (111, 134, 151), metodologia (tabela e linha 76), resultados (linha 19 e tabela), conclusão (16), síntese (270) | Detalhar só na metodologia; nos outros lugares, mencionar de passagem. |
| Defasagens entre clima e casos | 2 seções | `referencial_teorico.tex:20` e seção "Defasagens Temporais" (`:100-102`) | Fundir em uma seção. |
| Clima e dengue no Brasil | 2 seções | "Relação entre Variáveis Climáticas" (`:14-18`) e "Estudos Sobre Clima e Dengue no Brasil" (`:94-98`), com as mesmas 3 citações | Fundir em uma seção. |
| Explicação do XGBoost | 4 vezes | Introdução (101), referencial (61-63, figura, 118-126), tabela comparativa | Manter a explicação técnica só na seção de gradient boosting. |
| Árvores não extrapolam e treino em log | 4 vezes | Referencial (126, 160), resultados (111), conclusão (8) | Explicar no referencial e só retomar nos resultados. |
| Persistência como referência forte | 3 vezes | Introdução (101), referencial (112-116), resultados | Reduzir na introdução. |
| Cegueira de dados "otimista" | 3 vezes | Metodologia (162), resultados (176), conclusão (23) | Manter na metodologia e nas limitações. |
| "Alertas devem vir da regressão" | 3 vezes | Resultados (236), sistema (36), conclusão (12) | Manter nos resultados e na conclusão. |
| Descrição clínica da dengue | longa | Cerca de 15 parágrafos de clínica e impacto social na introdução, herdados do TCC 1 | Resumir para 3 ou 4 parágrafos com fonte. |

## 4. Divisão dos ajustes

⏳ = depende da v4 rodada com o INMET corrigido.

### Thiago

- **Título, resumo e abstract:** trocar "municípios" por "mesorregiões" e reescrever com foco no momento do surto. ⏳ só nos números.
- **Introdução:** reformular problema, pergunta e objetivos com foco no momento do surto; explicar o que é mesorregião e por que foi usada; resumir a parte clínica; corrigir os itens 1, 2, 3, 7 e 8 das inconsistências.
- **Referencial:** nova subseção com bibliografia sobre por que é difícil prever o tamanho dos picos; nova subseção sobre clima fraco no curto prazo e o INMET como alternativa quando falta SINAN; fundir as seções repetidas; corrigir os itens 4, 5 e 9.
- **Metodologia (dados):** justificar a agregação por mesorregião (5.570 municípios × cerca de 700 estações) e manter as correções do INMET.
- **Metodologia (hiperparâmetros):** tabela explicando o que cada hiperparâmetro faz e por que tem aquele valor.
- **INMET corrigido:** reprocessar o INMET de 2000 a 2017 com o código corrigido e entregar os dados ao Pedro.
- **Cegueira de dados e métricas de momento na v4** (erro na semana do pico, acerto de direção).
- **Resultados:** comparação com os baselines (momento × tamanho), clima e cegueira de dados (inclui o item 6), recorte do DF. ⏳
- **Conclusão:** contribuições e limitações.
- **Fechamento:** figuras, `RASTREABILIDADE.md`, compilação final e PR.

### Pedro

- **Referencial:** subseção sobre séries longas e mudança dos dados ao longo do tempo (*drift*).
- **Metodologia (desenho da v4):** janelas de treino × conjuntos de atributos e divisão treino/validação/teste, com nomes descritivos no lugar de A/B/C.
- **Metodologia (avaliação):** *walk-forward*, curva de aprendizado, Optuna, PSI e classificação em 4 faixas de risco.
- **Rodar a v4 de novo** com o INMET corrigido, com os baselines no pipeline; confirmar o item 10.
- **Resultados da v4:** tabela principal, curva de aprendizado, *drift*, Optuna (por que não foi adotado), classificação, SHAP e *walk-forward*. ⏳
- **Figuras da v4.** ⏳
- **Sistema:** atualizar para o dashboard da v4 (fluxo semanal e sincronização com o HuggingFace).
- **Cronograma:** incluir outubro e novembro.
- **Conclusão:** limitações e trabalhos futuros técnicos (hiperparâmetros, outras janelas).
- **Notebooks do Kaggle:** usar os mesmos hiperparâmetros do pipeline, ajustar o baseline sazonal (mesma semana do ano anterior) e corrigir o resumo, que hoje diz que o XGBoost supera os baselines em todas as escalas.

### Regras

- Cada um edita só as próprias seções; nas seções divididas, cada um fica com subseções separadas.
- Os números do texto saem sempre dos relatórios do pipeline (`rodar_v4.sh`), não do Kaggle.
- O que não tem ⏳ pode começar já.
- Prioridade para a banca: item 1 (DF, 313 mil × 256 mil) e item 6 (cegueira de dados).
