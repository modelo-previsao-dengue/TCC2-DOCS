# Método Executado

## Pipeline aplicada

A execução foi realizada por uma pipeline dedicada, construída para o TCC2.

Fluxo implementado:

1. Resumo do que o TCC1 realmente utilizou.
2. Download dos arquivos anuais completos do SINAN.
3. Extração do recorte analítico configurado.
4. Normalização dos microdados.
5. Remoção de duplicatas exatas.
6. Agregação em nível de semana epidemiológica.
7. Clusterização das semanas.
8. Seleção de atributos baseada nos clusters.
9. Geração de artefatos de qualidade e evidências.

## Transformações executadas

- Padronização de datas
- Conversão de idade para anos
- Cálculo de atraso entre notificação e início dos sintomas
- Derivação de indicadores binários para:
  - sintomas
  - comorbidades
  - sinais de alarme
  - sinais de gravidade
  - classificação final
  - critério de confirmação
- Agregação semanal por média dos indicadores e contagem de notificações

## Modelos de análise executados

### 1. Clusterização por intensidade

Usa a variável `NOTIFICACOES` junto com os atributos derivados para separar semanas de baixa e alta transmissão.

### 2. Clusterização por perfil clínico-epidemiológico

Remove `NOTIFICACOES` do espaço de cluster para forçar a separação por características clínicas e epidemiológicas das semanas.

## Seleção de atributos

A seleção foi feita combinando:

- ANOVA (`f_classif`)
- informação mútua
- importância por `RandomForestClassifier`

Foi calculado um `composite_score` para ranquear os atributos e marcar os selecionados.
