# Documentacao do processo de clusterizacao e justificativa dos atributos

## Objetivo

Este documento descreve, de forma reprodutivel, como a clusterizacao de atributos climaticos foi aplicada e por que os atributos finais foram escolhidos para o modelo preditivo de dengue.

## Escopo desta rodada

- Base de entrada: data_processed/inmet_2022_2024.csv
- Script principal: scripts/cluster_inmet_attributes.py
- Artefatos gerados:
  - data_processed/inmet_feature_selection/clusters_inmet.csv
  - data_processed/inmet_feature_selection/selected_features_inmet.csv
  - data_processed/inmet_feature_selection/report.md

## Visao geral do metodo

A selecao foi estruturada em quatro blocos:

1. Preparacao temporal dos dados climaticos.
2. Engenharia de atributos (lags, medias moveis, acumulados e extremos).
3. Clusterizacao por similaridade de comportamento entre variaveis.
4. Escolha final de representantes por prioridade epidemiologica e balanceamento entre familias climaticas.

## Etapas detalhadas do processo

### 1) Preparacao dos dados

- Leitura da serie diaria INMET.
- Ordenacao por data.
- Agregacao para nivel semanal (week_start).

Resumo da agregacao semanal:

- chuva semanal (soma),
- temperatura media semanal (media),
- temperatura minima semanal (minimo),
- temperatura maxima semanal (maximo),
- umidade media semanal (media),
- pressao media semanal (media),
- vento medio semanal (media).

Tambem ha suporte para colunas opcionais, quando disponiveis na base:

- umidade minima e maxima,
- ponto de orvalho,
- radiacao,
- insolacao,
- rajada de vento.

### 2) Engenharia de atributos

Foram gerados atributos derivados para capturar memoria temporal e condicoes ambientais relevantes:

- lags de 1, 2, 4, 8 e 12 semanas,
- medias moveis e acumulados,
- amplitude termica,
- interacoes entre variaveis (chuva x temperatura, temperatura x umidade),
- indicadores de extremos:
  - dias de chuva intensa na semana (rain >= 10 mm),
  - maior sequencia de dias secos na semana (rain <= 1 mm).

### 3) Clusterizacao

A clusterizacao foi feita sobre colunas numericas apos padronizacao:

- padronizacao: StandardScaler,
- similaridade: correlacao absoluta entre atributos,
- distancia: distance = 1 - |corr|,
- algoritmo: clusterizacao hierarquica aglomerativa (average linkage),
- corte: distance_threshold = 0.55.

Essa estrategia reduz colinearidade mantendo interpretabilidade, pois concentra variaveis muito parecidas no mesmo cluster.

### 4) Selecao de representantes

Em cada cluster, os candidatos foram ranqueados por score de prioridade e estabilidade de disponibilidade (menos ausencias).

Depois, foi aplicado balanceamento por familia de variaveis para evitar dominancia de uma unica familia.

Familias climaticas consideradas:

- precipitacao,
- temperatura,
- umidade,
- radiacao (quando disponivel),
- pressao,
- vento.

## Atributos de data e localizacao (complementares)

Os atributos abaixo nao sao o foco da clusterizacao climatica, mas sao essenciais para o painel espaco-temporal e para o treinamento final do modelo.

### Atributos de data

- date: data diaria de observacao meteorologica (entrada bruta INMET).
- week_start: data de inicio da semana usada na agregacao semanal.
- iso_year: ano epidemiologico ISO para chave temporal semanal.
- iso_week: semana epidemiologica ISO para chave temporal semanal.
- sem_not: semana de notificacao epidemiologica (quando disponivel na base integrada).

### Atributos de localizacao

- ibge_mun: codigo do municipio IBGE, chave espacial principal para merge SINAN + INMET.
- uf: unidade federativa para agregacoes regionais e avaliacao por estado.
- municipio: nome do municipio para rastreabilidade e auditoria.

### Papel metodologico desses atributos

- Chave de merge recomendada: ibge_mun + iso_year + iso_week.
- Chave alternativa de apoio: uf + municipio (normalizados), quando nao houver ibge_mun.
- Uso no modelo: particionamento temporal, validacao por recorte geografico e analise de desempenho por UF/municipio.

## Resultado da ultima execucao

- Observacoes semanais: 158
- Clusters encontrados: 10
- Atributos recomendados: 7

Atributos selecionados:

1. rain_heavy_days_lag2
2. rain_heavy_days_lag4
3. humidity_mean_lag2
4. temp_mean_lag2
5. temp_mean_lag4
6. pressure_lag2
7. wind_speed_lag2

## Justificativa da escolha dos atributos

### rain_heavy_days_lag2 e rain_heavy_days_lag4

Justificativa:

- Capturam extremos de precipitacao recentes e de medio prazo.
- Chuva intensa influencia acumulacao de agua parada e condicoes de criadouros.
- Lags de 2 e 4 semanas sao coerentes com atraso biologico entre condicao ambiental e aumento de casos notificados.

### humidity_mean_lag2

Justificativa:

- Umidade elevada favorece sobrevivencia do vetor e dinamica de transmissao.
- Lag de 2 semanas representa resposta de curto prazo da serie epidemiologica as mudancas ambientais.

### temp_mean_lag2 e temp_mean_lag4

Justificativa:

- Temperatura modula ciclo de vida do mosquito e velocidade de desenvolvimento viral.
- Lags curtos e intermediarios capturam efeitos rapidos e persistentes.
- A presenca simultanea de lag2 e lag4 aumenta cobertura temporal sem depender apenas de um unico horizonte.

### pressure_lag2

Justificativa:

- Pressao funciona como proxy de padroes atmosfericos associados ao regime de chuva e estabilidade do tempo.
- Mesmo com menor prioridade epidemiologica direta, adiciona sinal complementar util para reduzir perda de informacao macroclimatica.

### wind_speed_lag2

Justificativa:

- Vento pode afetar dispersao local do vetor e dinamica microambiental.
- Entrou como variavel de diversidade de familia, evitando que o modelo dependa apenas de chuva, temperatura e umidade.

## Por que radiacao e insolacao nao entraram na selecao final

Nesta execucao, radiacao e insolacao nao estavam disponiveis na base de entrada utilizada. Por isso, nao participaram da disputa de representatividade.

Importante: o pipeline ja esta preparado para incorporar essas variaveis automaticamente quando elas estiverem presentes no CSV de entrada.

## Racional metodologico da escolha final

A escolha final combina tres criterios ao mesmo tempo:

1. Reduzir redundancia (clusterizacao por correlacao).
2. Preservar variaveis climaticas com maior plausibilidade epidemiologica.
3. Manter diversidade de familias para aumentar robustez preditiva.

Em termos praticos, isso evita dois extremos:

- excesso de variaveis altamente colineares,
- conjunto muito pequeno e sem cobertura dos principais mecanismos climaticos da dengue.

## Como usar no modelo final

- Usar os 7 atributos selecionados como bloco exogeno inicial.
- Treinar com validacao temporal (janela deslizante ou blocos temporais).
- Medir desempenho global e por recorte geografico (UF e municipio).
- Ao disponibilizar radiacao/insolacao no dado de entrada, rerodar a selecao e comparar ganho incremental.

## Reproducao

Com ambiente Python ativo, executar:

python scripts/cluster_inmet_attributes.py

O comando sobrescreve os arquivos em data_processed/inmet_feature_selection com os resultados da rodada mais recente.
