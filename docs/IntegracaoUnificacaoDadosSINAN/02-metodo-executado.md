# Método Executado

## Pipeline

A task foi executada por um script dedicado:

- `TCC2-DOCS/scripts/integrate_unify_sinan_data.py`

## Navegação e validação das fontes

Antes da integração, foi feita a conferência das fontes e do escopo:

1. Portal inicial do SINAN:
   - `https://portalsinan.saude.gov.br/`
   - confirmação da estrutura oficial do sistema e da área de acesso a dados epidemiológicos
2. Página `Dados Epidemiológicos Sinan`:
   - `https://portalsinan.saude.gov.br/dados-epidemiologicos-SINAN`
   - confirmação de que o portal organiza o acesso por tabulações DATASUS e grupos de agravos
3. Catálogo oficial OpenDataSUS de dengue:
   - `https://opendatasus.saude.gov.br/dataset/arboviroses-dengue`
   - confirmação de recursos anuais CSV/JSON/XML e dicionário de dados do dengue
4. Base dos Dados:
   - `https://basedosdados.org/dataset/f51134c2-5ab9-4bbc-882f-f1034603147a`
   - confirmação da cobertura temporal ampla e disponibilidade tratada, usada apenas como referência complementar
5. Material executado do `TCC1`:
   - validação do recorte efetivo `Distrito Federal/Brasília`, `2022-2024`, e da existência de uma base unificada semanal já consolidada

## Etapas realizadas

1. Carregamento do recorte normalizado do SINAN.
2. Carregamento da base semanal do SINAN.
3. Carregamento dos clusters de intensidade e perfil clínico do SINAN.
4. Reconstrução do calendário semanal do SINAN a partir de `ANO_SEMANA`, para evitar deriva causada por datas individuais inconsistentes.
5. Carregamento da base diária do INMET (`2022-2024`).
6. Agregação do INMET para semanas iniciadas no domingo.
7. Cálculo de atributos climáticos semanais:
   - soma de chuva
   - média de chuva
   - temperatura média, mínima e máxima
   - amplitude térmica
   - umidade média
   - pressão média
   - velocidade média do vento
   - número de dias com chuva
8. Junção semanal `SINAN + INMET`.
9. Comparação direta com `TCC1-DOCS/data_processed/dataset_unificado.csv`.
10. Geração de artefatos de qualidade, rastreabilidade e evidências.

## Estrutura do dataset final

O dataset final preserva:

- atributos semanais do SINAN
- variáveis climáticas do INMET
- labels de cluster do SINAN
- calendário epidemiológico
- campos suficientes para reconciliar a série nova com a base unificada do `TCC1`

## Critérios de qualidade aplicados

- checagem de linhas semanais duplicadas
- checagem de cobertura temporal
- checagem de semanas do SINAN sem match climático
- checagem de missing por coluna
- checagem de alinhamento temporal com o `TCC1`
- checagem de correlação entre variáveis climáticas equivalentes do `TCC1` e do dataset final
