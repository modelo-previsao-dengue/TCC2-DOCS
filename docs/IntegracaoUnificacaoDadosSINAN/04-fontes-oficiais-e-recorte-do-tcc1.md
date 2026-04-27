# Fontes Oficiais e Recorte do TCC1

## O que foi navegado no SINAN

As fontes revisadas para esta task foram:

- Portal institucional do SINAN: `https://portalsinan.saude.gov.br/`
- Página oficial `Dados Epidemiológicos Sinan`: `https://portalsinan.saude.gov.br/dados-epidemiologicos-SINAN`
- Catálogo OpenDataSUS de dengue: `https://opendatasus.saude.gov.br/dataset/arboviroses-dengue`
- Base dos Dados do SINAN: `https://basedosdados.org/dataset/f51134c2-5ab9-4bbc-882f-f1034603147a`
- Dicionário oficial de dados do dengue: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/dic_dados_dengue.pdf`

## O que essas fontes indicam

1. O portal do SINAN organiza o acesso institucional e aponta a área oficial de dados epidemiológicos.
2. A página de dados epidemiológicos do SINAN prioriza tabulações DATASUS e acesso por grupos de doenças e agravos.
3. O OpenDataSUS é a fonte oficial mais adequada para microdados anuais de dengue, com recursos anuais em `CSV`, `JSON` e `XML`.
4. A Base dos Dados confirma a cobertura temporal ampla do SINAN e a existência de uma camada tratada, mas nesta task ela foi usada como referência complementar, não como fonte principal de integração.

## O que foi encontrado no TCC1

O `TCC1` possui dois níveis de escopo:

- objetivo geral planejado: municípios brasileiros
- execução consolidada no material entregue: `Distrito Federal/Brasília`, `2022-2024`

Isso aparece no material executado do `TCC1` de forma consistente:

- introdução e resumo focados no `Distrito Federal`
- considerações finais afirmando que a base unificada consolidada cobre `2022-2024`
- existência de `TCC1-DOCS/data_processed/dataset_unificado.csv` com `156` semanas

## Decisão final desta task

Por coerência metodológica, a integração e unificação do SINAN nesta etapa foi feita no mesmo recorte que o `TCC1` efetivamente consolidou:

- área: `Brasília/DF`
- período: `2022-2024`
- granularidade: `semana epidemiológica`

Essa decisão evita misturar:

- um objetivo nacional ainda não consolidado em base única no projeto
- com uma entrega de integração que precisava ser real, rastreável e imediatamente utilizável na modelagem do `TCC2`
