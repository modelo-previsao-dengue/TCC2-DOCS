# Comparacao de Modelos: XGBoost vs SARIMA

## 1. Visao Geral

Este repositorio implementa duas baselines educacionais de previsao para casos semanais de dengue em Brasilia: um regressor `XGBoost` e um modelo de series temporais `SARIMA`. Ambos os notebooks usam o mesmo conjunto de dados unificado, mas representam filosofias de modelagem diferentes.

O notebook de XGBoost constroi um pipeline de aprendizado supervisionado com contagens defasadas de dengue, estatisticas moveis, indicadores sazonais e covariaveis climaticas como chuva, temperatura, umidade e pressao. O notebook de SARIMA modela a serie de contagem de dengue como um processo sazonal univariado e, na implementacao atual, nao inclui variaveis climaticas exogenas.

Para o objetivo do TCC descrito em `README.md`, a pergunta central nao e apenas qual notebook reporta menor erro, mas qual abordagem esta mais alinhada com a previsao de surtos de dengue usando tanto dinamica temporal quanto informacoes climaticas em multiplos municipios.

## 2. Modelo XGBoost

### Como funciona neste projeto

O notebook `notebooks/examples/02_xgboost_model_educativo.ipynb` trata a previsao como um problema de regressao. Ele carrega o conjunto de dados semanal unificado, verifica o alinhamento temporal e mantem variaveis epidemiologicas e climaticas no espaco de atributos.

As principais etapas de preprocessamento e modelagem sao:

- Criacao de lags de 1 a 12 semanas para casos de dengue e variaveis climaticas.
- Criacao de atributos derivados, como medias moveis, desvios padrao moveis, variacoes percentuais, indicadores sazonais, semana do ano e termos de interacao.
- Divisao cronologica em conjuntos de treino, validacao e teste (`60% / 20% / 20%`) para reduzir vazamento de informacao.
- Treinamento de `XGBRegressor` com early stopping.
- Ajuste adicional de hiperparametros com `GridSearchCV` e `TimeSeriesSplit`, embora as metricas finais reportadas sejam calculadas com `xgb_model`, e nao com `xgb_model_tuned`.
- Interpretabilidade basica por meio de importancia de atributos e SHAP.

### Pontos fortes

- Atende diretamente ao objetivo do projeto de combinar historico de dengue com dados climaticos.
- Captura relacoes nao lineares e interacoes que sao dificeis de expressar em modelos classicos lineares de series temporais.
- Inclui engenharia de atributos explicita para sazonalidade e memoria temporal de curto prazo.
- Fornece interpretabilidade pratica por meio de importancia de atributos e SHAP.
- E mais adaptavel a um cenario com multiplos municipios porque o mesmo pipeline de atributos pode ser reutilizado em diferentes bases.
- Ja inclui uma classe reutilizavel (`ModeloPreditoXGBoost`) pensada para extensao a varias cidades.

### Pontos fracos

- Depende fortemente da qualidade da engenharia de atributos.
- O desempenho de validacao reportado e fraco, o que sugere instabilidade ou overfitting apesar do excelente ajuste no treino.
- O notebook ainda nao implementa a validacao rolling-window recomendada no `README.md`.
- Modelos baseados em arvores costumam ser menos transparentes do que modelos estatisticos classicos no nivel dos parametros.

## 3. Modelo SARIMA

### Como funciona neste projeto

O notebook `notebooks/examples/03_sarima_model_educativo.ipynb` modela a incidencia de dengue como uma serie semanal sazonal univariada. Ele reamostra os dados para frequencia semanal, decompoe a serie, executa um teste ADF de estacionariedade, inspeciona ACF/PACF e treina um objeto `SARIMAX` configurado como um modelo SARIMA com ordem `(1,1,1)` e ordem sazonal `(1,1,0,52)`.

As principais etapas sao:

- Agregacao semanal apenas dos casos de dengue.
- Verificacao de estacionariedade com ADF, que indica nao estacionariedade antes da diferenciacao.
- Especificacao manual das ordens do SARIMA com base em diagnosticos de series temporais.
- Divisao cronologica em conjuntos de treino e teste (`80% / 20%`).
- Geracao de previsoes para o periodo de teste.
- Diagnostico de residuos, com uma alternativa manual porque o grafico diagnostico padrao nao e suportado pelo tamanho da amostra e pela estrutura de lags disponiveis.

### Pontos fortes

- E uma baseline forte para previsao sazonal univariada.
- E mais interpretavel do ponto de vista estatistico no nivel dos parametros do modelo.
- Exige menos atributos engenheirados do que o XGBoost.
- E util como benchmark para quantificar quanto valor as covariaveis climaticas agregam.

### Pontos fracos

- O notebook atual ignora variaveis climaticas, o que o desalinha do objetivo central do TCC.
- Assume uma estrutura sazonal linear relativamente estavel e e mais sensivel a escolhas de especificacao.
- Escalar para muitos municipios normalmente exige selecao manual repetida de ordens ou busca automatizada de SARIMA.
- E menos flexivel para modelar interacoes nao lineares entre clima e dengue.
- O proprio notebook sugere SARIMAX como proximo passo, indicando que o SARIMA puro ainda nao e o modelo final pretendido.

## 4. Comparacao Quantitativa

Os notebooks nao usam exatamente o mesmo protocolo de avaliacao, entao as metricas abaixo devem ser interpretadas com cautela. O XGBoost usa uma divisao `60/20/20` entre treino, validacao e teste, com 30 observacoes de teste apos remover as 12 linhas iniciais de lag. O SARIMA usa uma divisao `80/20` entre treino e teste, com 32 observacoes de teste na serie semanal completa.

| Modelo | RMSE Treino | RMSE Validacao | RMSE Teste | MAE Treino | MAE Validacao | MAE Teste | MAPE Treino | MAPE Validacao | MAPE Teste | R² Treino | R² Validacao | R² Teste |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| XGBoost | 5.50 | 11144.50 | 243.72 | 2.24 | 7910.77 | 230.16 | 0.20 | 51.65 | 53.00 | 1.00 | -0.68 | 0.35 |
| SARIMA | nao reportado | nao reportado | 1976.18 | nao reportado | nao reportado | 1693.90 | nao reportado | nao reportado | nao reportado | nao reportado | nao reportado | -7.432 |

Principais observacoes:

- Na divisao de teste reportada, o XGBoost supera claramente o SARIMA em RMSE, MAE e R².
- O SARIMA nao reporta MAPE no notebook.
- O XGBoost mostra uma grande diferenca entre desempenho de treino e validacao, o que indica que a configuracao atual ainda precisa de uma validacao temporal mais forte antes de qualquer afirmacao empirica final.
- Mesmo com essa ressalva, os resultados de teste do SARIMA sao substancialmente piores no estado atual do repositorio.

## 5. Comparacao Qualitativa

### Tratamento de series temporais

O SARIMA e um modelo nativo de series temporais e lida diretamente com tendencia e sazonalidade anual por meio de diferenciacao e termos sazonais. O XGBoost lida com dependencia temporal de forma indireta, usando atributos defasados e estatisticas moveis. Na pratica, ambas as abordagens conseguem modelar estrutura temporal, mas o SARIMA e mais natural para sazonalidade puramente univariada, enquanto o XGBoost e mais flexivel quando ha preditores mais ricos disponiveis.

### Integracao de variaveis climaticas

Este e o ponto decisivo para o TCC. O `README.md` define o projeto como previsao de surtos de dengue usando series temporais combinadas com dados climaticos. O XGBoost ja faz isso. O notebook de SARIMA nao faz; ele modela apenas as contagens de dengue. Para se alinhar ao objetivo do projeto, o SARIMA precisaria evoluir para SARIMAX com regressores exogenos.

### Complexidade

O SARIMA e conceitualmente mais simples de especificar, mas pode se tornar dificil de ajustar quando ordens sazonais precisam ser escolhidas para muitos municipios. O XGBoost tem um pipeline de preprocessamento mais complexo, mas essa complexidade e programatica e mais facil de automatizar depois de padronizada.

### Interpretabilidade

O SARIMA e mais interpretavel no sentido estatistico classico porque seus coeficientes descrevem diretamente a estrutura autorregressiva e de medias moveis. O XGBoost e menos transparente internamente, mas o notebook compensa isso com importancia de atributos e SHAP, que costumam ser mais uteis para suporte a decisao aplicado quando muitos preditores estao envolvidos.

### Escalabilidade

O XGBoost e mais escalavel para um fluxo nacional ou com varios municipios. O repositorio ja inclui uma classe modular para reutilizacao, e o pipeline de engenharia de atributos pode ser padronizado entre cidades. O SARIMA e viavel como baseline, mas manter e ajustar muitos modelos sazonais especificos por municipio exigiria mais trabalho.

### Facilidade de manutencao e extensao

O XGBoost e mais facil de estender com novas variaveis, novos lags ou alvos alternativos, como classes de risco de surto. O SARIMA e mais dificil de estender alem do cenario univariado, a menos que o projeto migre explicitamente para SARIMAX ou outro framework multivariado de series temporais.

### Robustez a dados ausentes ou ruidosos

O notebook de XGBoost verifica explicitamente valores ausentes e aplica interpolacao linear quando necessario. Metodos baseados em arvores tambem tendem a ser mais tolerantes a preditores heterogeneos e padroes nao lineares imperfeitos. O SARIMA geralmente exige uma serie temporal mais limpa e estavel, e suas premissas o tornam mais sensivel a dados ausentes, quebras estruturais e estrutura sazonal mal especificada.

## 6. Recomendacao Final

O modelo mais adequado para o objetivo atual do TCC e o **XGBoost**.

A recomendacao se baseia em duas camadas de evidencia. Primeiro, o XGBoost esta mais alinhado com o objetivo declarado do projeto em `README.md`, que enfatiza explicitamente a previsao de dengue com dados climaticos. O notebook ja integra chuva, temperatura, umidade e pressao junto com atributos temporais. Segundo, os resultados quantitativos atualmente reportados sao substancialmente melhores do que a baseline SARIMA nas avaliacoes de teste disponiveis: o XGBoost alcanca `RMSE = 243.72`, `MAE = 230.16` e `R² = 0.35`, enquanto o SARIMA reporta `RMSE = 1976.18`, `MAE = 1693.90` e `R² = -7.432`.

Isso nao significa que o SARIMA deva ser descartado. Ele continua sendo uma baseline estatistica util e uma forte referencia para previsao guiada por sazonalidade. No entanto, em sua forma atual, nao e o melhor candidato final para este TCC porque ainda nao incorpora variaveis climaticas exogenas, que sao centrais para a definicao do problema.

## 7. Proximos Passos

- Reavaliar o XGBoost com validacao rolling-window ou walk-forward, como recomendado no `README.md`, para obter estimativas mais confiaveis de generalizacao temporal.
- Avaliar o modelo XGBoost ajustado (`xgb_model_tuned`) no conjunto de teste separado, ja que o notebook atualmente reporta metricas finais para o `xgb_model` sem ajuste.
- Adicionar depois metricas explicitas de classificacao de surtos se o projeto converter previsoes em niveis de alerta (`AUC`, `Precision`, `Recall`, `F1-score`).
- Refinar o pipeline de atributos do XGBoost com janelas alternativas de lag, novas variaveis derivadas e testes de selecao de atributos.
- Comparar o XGBoost com variantes do proprio modelo, por exemplo:
  - `XGBoost` com diferentes janelas temporais e horizontes de previsao.
  - `XGBoost` com ajuste mais robusto de hiperparametros.
  - `XGBoost` com novas covariaveis climaticas e epidemiologicas.
  - `LSTM` ou outros modelos sequenciais quando o protocolo de validacao estiver estavel.

Em resumo, o repositorio deve tratar o **XGBoost como principal candidato de modelo** para a proxima fase do TCC.
