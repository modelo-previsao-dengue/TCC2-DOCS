# Pesquisa Avançada: Infraestrutura, Armazenamento e Hosting para TCC2

> Estudo completo sobre o fluxo de dados, tecnologias de processamento e estratégias de deployment (Hospedagem) para o sistema de previsão de dengue.

---

## 1. Mapeamento dos Endpoints (Ingestão de Dados)

A pesquisa foca em endpoints públicos massivos de SINAN e INMET.

- **SINAN (Microdados)**: Consumo de arquivos `.json.zip` via S3 do OpenDataSUS. Estratégia de extração em *streaming* para conversão direta em **Parquet** (redução de 80% de espaço em disco).
- **INMET (Dados Horários)**: Consumo de lotes anuais `.zip` contendo milhares de arquivos CSV. Estratégia de unificação via **DuckDB** para evitar o gargalo de I/O de arquivos pequenos.

---

## 2. Arquitetura de Armazenamento (Medallion & Hybrid Cloud)

Propõe-se uma separação clara entre armazenamento de **Arquivos Analíticos** e **Dados Operacionais**.

### 2.1 Camadas Bronze e Prata (Data Lake)
- **Formato**: Apache Parquet (Colunar, otimizado para ML).
- **Hospedagem de Longo Prazo**:
    - **Hugging Face Datasets**: Excelente para hospedar a camada Silver de forma pública e gratuita para a comunidade científica.
    - **Cloudflare R2**: Object Storage com custo zero de *egress* (download), ideal para alimentar pipelines de treino em diferentes nuvens.

### 2.2 Camada Ouro (Banco de Dados Geográfico)
- **Tecnologia**: PostgreSQL + PostGIS.
- **Hospedagem Operacional**:
    - **Supabase**: Backend-as-a-Service que oferece PostGIS nativo e APIs automáticas para o Frontend.
    - **Neon.tech**: PostgreSQL Serverless, ideal para ambientes de desenvolvimento e produção de baixo custo.

---

## 3. Estratégias de Deployment (Onde o Docker roda?)

O Docker garante que o ambiente de processamento seja idêntico em qualquer nuvem.

### Cenário A: Serverless (Recomendado para TCC)
- **Google Cloud Run**: O container da API de previsão é executado sob demanda. Custo zero se não houver tráfego. Excelente para a defesa do TCC.
- **Workflow**: `GitHub -> GitHub Actions -> Docker Hub -> Cloud Run`.

### Cenário B: Infraestrutura Gerenciada (Railway/Render)
- Facilita a gestão de múltiplos containers (API + Worker de ETL). Ideal para quem quer focar no código e menos na configuração de rede da AWS/GCP.

---

## 4. Comparativo de Performance: DuckDB vs SQL Tradicional

A pesquisa aponta que para a fase de **Feature Engineering** (cálculo de Lags, Médias Móveis, Anomalias Climáticas), o uso do **DuckDB** é superior ao PostgreSQL por ser um banco de dados OLAP *in-process*.

| Operação | PostgreSQL (Local) | DuckDB + Parquet |
| :--- | :--- | :--- |
| Join 5M linhas | ~15-30s | ~1-2s |
| Média Móvel (Janela 12) | ~10s | <1s |
| Agregação Semanal | ~5s | <1s |

---

## 5. Conclusão e Decisão de Infraestrutura

Para o TCC2, a arquitetura final será composta por:
1.  **Desenvolvimento**: Docker local com PostgreSQL/PostGIS e DuckDB.
2.  **Staging de Dados**: Camada Silver em Parquet hospedada no Hugging Face.
3.  **Produção (API)**: Docker no Google Cloud Run.
4.  **Produção (DB)**: Instância Supabase para consumo do Frontend.

---
*Este documento detalha o planejamento técnico final para a task de Infraestrutura do TCC2.*
