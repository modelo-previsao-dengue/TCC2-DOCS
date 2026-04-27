# Visão Geral da Task

## Objetivo

Executar de forma completa a etapa `Coleta e Processamento de Dados - SINAN`, substituindo o recorte simplificado do TCC1 por uma coleta real dos microdados oficiais do SINAN e gerando uma base organizada para uso no TCC2.

## Fontes reais utilizadas

- Portal SINAN: `https://portalsinan.saude.gov.br/dados-epidemiologicos-SINAN`
- OpenDataSUS / S3: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/json/`
- Dicionário de dados: `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/dic_dados_dengue.pdf`
- Base dos Dados: `https://basedosdados.org/dataset/f51134c2-5ab9-4bbc-882f-f1034603147a`

## Relação com o TCC1

O TCC1 documentava a análise como `Distrito Federal`, mas o código executado na prática usava:

- `geocode 5300108`
- `Brasília/DF`
- `2022-2024`
- série agregada da API `InfoDengue`

Para o TCC2, a task foi refeita com microdados reais do SINAN, preservando o mesmo recorte temporal e espacial de referência para manter comparabilidade.

## Recorte final adotado

- Município de referência: `Brasília/DF`
- Código de referência: `5300108`
- Período: `2022-2024`

## Entregáveis desta task

- recorte real do SINAN filtrado e normalizado
- atributos semanais derivados do SINAN
- clusterização por intensidade de transmissão
- clusterização por perfil clínico-epidemiológico
- seleção de atributos em ambos os modos
- evidências de qualidade e execução
