# Resultados e Evidências

## Volumetria final

- Registros normalizados no recorte final: `399.094`
- Semanas epidemiológicas: `156`
- Cobertura temporal: `2022-01-02` até `2024-12-28`

Distribuição anual:

- `2022`: `73.245`
- `2023`: `43.127`
- `2024`: `283.712`

## Qualidade dos dados

- Linhas duplicadas exatas no recorte final: `0`
- Semanas duplicadas: `0`
- Missing nos campos-chave monitorados: `0%`
  - `DT_NOTIFIC`
  - `DT_SIN_PRI`
  - `SEM_PRI`
  - `CS_SEXO`
  - `CS_RACA`
  - `CLASSI_FIN`
  - `CRITERIO`
  - `HOSPITALIZ`
  - `EVOLUCAO`

## Clusterização por intensidade

- Melhor `k`: `2`
- Silhouette: `0.125845`

Clusters:

- `baixa_transmissao`: `135` semanas, média `944,1` notificações
- `transicao`: `21` semanas, média `12.935,4` notificações

Principais atributos:

- `NOTIFICACOES`
- `dor_retro_flag`
- `febre_flag`
- `cefaleia_flag`
- `criterio_clinico_epi`
- `nausea_flag`
- `artralgia_flag`
- `criterio_lab`

## Clusterização por perfil clínico-epidemiológico

- Melhor `k`: `6`
- Silhouette: `0.106929`

Clusters:

- `perfil_basal`: `24` semanas
- `perfil_intermediario`: `24` semanas
- `perfil_alterado`: `48` semanas
- `perfil_agudo`: `25` semanas
- `perfil_extremo`: `22` semanas
- `perfil_raro`: `13` semanas

Principais atributos:

- `raca_parda`
- `cefaleia_flag`
- `criterio_lab`
- `nausea_flag`
- `dor_retro_flag`
- `leucopenia_flag`
- `exantema_flag`
- `febre_flag`

## Evidências incluídas nesta pasta

- `evidencias/quality_summary_brasilia_2022_2024.json`
- `evidencias/cluster_evaluation_brasilia_2022_2024.csv`
- `evidencias/cluster_evaluation_profile_brasilia_2022_2024.csv`
- `evidencias/selected_features_brasilia_2022_2024.json`
- `evidencias/selected_features_profile_brasilia_2022_2024.json`

## Conclusão da task

A task `Coleta e Processamento de Dados - SINAN` foi executada com dados reais, organizada em pipeline reproduzível e documentada com evidências verificáveis.
