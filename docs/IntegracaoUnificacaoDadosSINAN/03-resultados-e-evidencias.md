# Resultados e Evidências

## Resultado da unificação

Foi gerado um dataset semanal unificado real entre SINAN e INMET para Brasília/DF no período `2022-2024`.

## Volumetria final

- Linhas do dataset final: `156`
- Colunas do dataset final: `101`
- Cobertura temporal: `2022-01-02` até `2024-12-22`
- Semanas agregadas do INMET antes da junção: `158`

## Qualidade da junção

- Semanas do SINAN sem correspondência climática: `0`
- Percentual de match completo: `100%`
- `ANO_SEMANA` duplicado no dataset final: `0`
- `week_start` duplicado no dataset final: `0`

## Alinhamento com o TCC1

- Semanas sobrepostas com `dataset_unificado.csv`: `156`
- Correlação entre `casos_dengue` do `TCC1` e `NOTIFICACOES` do novo dataset: `0.999229`
- Correlação entre chuva semanal das duas bases: `0.925975`
- Correlação entre temperatura média semanal das duas bases: `0.999994`
- Correlação entre umidade média semanal das duas bases: `0.999994`
- Correlação entre pressão média semanal das duas bases: `0.999991`

Os totais de casos não são idênticos:

- total do `TCC1`: `463.560`
- total do novo dataset: `399.094`

Essa diferença é esperada porque o `TCC1` consolidou uma base epidemiológica agregada anterior, enquanto esta task integrou o recorte semanal reconstruído a partir do microdado bruto processado do SINAN.

## O que entrou no dataset unificado

### Bloco SINAN

- contagem semanal de notificações
- atributos clínicos e epidemiológicos agregados por semana
- clusters de intensidade
- clusters de perfil clínico

### Bloco INMET

- chuva semanal
- temperatura média, mínima e máxima
- amplitude térmica
- umidade média
- pressão média
- velocidade média do vento
- dias com chuva

## Evidências incluídas

- `evidencias/dataset_unificado_sinan_inmet_brasilia_2022_2024.csv`
- `evidencias/quality_summary_integracao_unificacao_sinan.json`
- `evidencias/quality_missingness_integracao_unificacao_sinan.csv`
- `evidencias/comparacao_com_tcc1_dataset_unificado.csv`
- `evidencias/source_lineage_integracao_unificacao_sinan.json`
- `evidencias/schema_dataset_unificado_sinan_inmet.json`
- `evidencias/relatorio_integracao_unificacao_sinan.md`

## Conclusão

A task `Integração e Unificação de Dados - SINAN` foi concluída com integração real, organizada e validada entre o recorte semanal do SINAN e a base climática do INMET, com rastreabilidade das fontes oficiais e comparação explícita com a base unificada do `TCC1`.
