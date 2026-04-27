# Visão Geral da Task

## Objetivo

Executar a integração e unificação real entre:

- a base semanal do SINAN já processada para Brasília/DF (`2022-2024`)
- a base climática diária do INMET agregada para o mesmo recorte semanal

## Fontes utilizadas

- SINAN oficial: portal institucional, área de dados epidemiológicos e catálogo OpenDataSUS de dengue
- SINAN processado: saída da task `Coleta e Processamento de Dados - SINAN`
- Base dos Dados: usada como referência de cobertura e disponibilidade tratada do SINAN
- INMET: `TCC1-DOCS/data_processed/inmet_2022_2024.csv`
- Base unificada do TCC1: `TCC1-DOCS/data_processed/dataset_unificado.csv`

## Decisão metodológica de escopo

O objetivo geral do trabalho no `TCC1` foi definido para municípios brasileiros, mas o recorte efetivamente consolidado no material executado do `TCC1` foi `Distrito Federal/Brasília`, no triênio `2022-2024`.

Por isso, nesta task a integração foi feita no mesmo recorte real já entregue, em vez de forçar uma expansão nacional sem base consolidada equivalente dentro do projeto atual.

## Chave de integração

A integração foi feita por:

- `ANO_SEMANA`
- `week_start`

O `week_start` foi reconstruído a partir de `ANO_SEMANA` com início no domingo, mantendo compatibilidade com a agregação semanal usada na base climática e com o dataset unificado do `TCC1`.

## Entrega esperada

- dataset semanal unificado
- validação de qualidade da junção
- esquema das colunas
- comparação com a base unificada do `TCC1`
- rastreabilidade das fontes oficiais usadas
- documentação e evidências da task
