# Relatório de Integração e Unificação de Dados - SINAN

## Escopo

- Recorte: Brasília/DF
- Código de referência: 5300108
- Período: 2022-2024

## Fontes integradas

- SINAN processado semanalmente a partir do microdado oficial
- INMET diário agregado para semana epidemiológica compatível
- Base unificada do TCC1 usada como referência de alinhamento

## Volumetria

- Linhas semanais do dataset final: 156
- Colunas do dataset final: 101
- Cobertura temporal: 2022-01-02 até 2024-12-22

## Qualidade da junção

- Semanas do SINAN sem correspondência climática: 0
- Percentual de match completo: 100.0%
- `ANO_SEMANA` duplicado no dataset final: 0
- `week_start` duplicado no dataset final: 0

## Estrutura final

O dataset unificado final contém:

- atributos semanais do SINAN
- calendário epidemiológico
- clusters de intensidade e perfil clínico
- variáveis climáticas semanais do INMET

## Principais colunas climáticas integradas

- `rain_sum`
- `rain_mean`
- `temp_mean`
- `temp_min`
- `temp_max`
- `temp_range`
- `humidity_mean`
- `pressure_mean`
- `wind_speed_mean`
- `rain_nonzero_days`

## Alinhamento com o TCC1

- Semanas sobrepostas com `dataset_unificado.csv`: 156
- Correlação entre `casos_dengue` do TCC1 e `NOTIFICACOES` do novo dataset: 0.999229
- Total do TCC1: 463560
- Total do novo dataset: 399094
- Diferença total: 64466

A diferença de total não invalida a integração: ela reflete que o TCC1 usou uma base agregada anterior, enquanto esta task integra o recorte semanal reconstruído a partir do microdado bruto processado do SINAN.