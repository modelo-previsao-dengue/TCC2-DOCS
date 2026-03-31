# Propostas de Arquitetura de Dados e Infraestrutura - TCC2

**Trabalho:** Desenvolvimento de um Modelo de Previsão para Surtos de Dengue  
**Autor:** Filippo Ferrari  
**Objetivo:** Definir o fluxo completo de dados (ingestão, processamento, armazenamento e hospedagem) para a fase de implementação do TCC2.

---

## 1. Contexto dos Dados
O sistema consome dados de duas fontes públicas principais com alta volumetria:
- **SINAN (Epidemiológico):** Microdados em arquivos `.json.zip` via S3 do OpenDataSUS (~500MB/ano).
- **INMET (Climático):** Dados horários em arquivos `.zip` contendo milhares de CSVs (~500 estações automáticas).
- **Processamento:** Exige a unificação de séries temporais por município-semana e cálculos de variáveis defasadas (lags).

---

## 2. Opção 1: Arquitetura "Scientific & Zero Cost" (Cloud-Native Serverless)
*Foco em ferramentas gratuitas, visibilidade acadêmica e baixa manutenção de servidor.*

### Fluxo de Dados:
1.  **Ingestão (ETL):** **GitHub Actions**. Scripts Python agendados realizam o download dos ZIPs, processam o JSON/CSV em memória e convertem para o formato **Apache Parquet**.
2.  **Hospedagem de Arquivos (Bronze/Silver):** **Hugging Face Datasets**. Os arquivos Parquet processados são armazenados em repositórios LFS no Hugging Face. Isso garante versionamento científico e acesso público/privado gratuito.
3.  **Banco de Dados (Gold):** **Supabase (PostgreSQL + PostGIS)**. Armazena os dados agregados prontos para consumo. O Supabase fornece APIs REST/GraphQL nativas sobre as tabelas.
4.  **Hospedagem da API (Previsão):** **Google Cloud Run**. O container Docker com o modelo de IA (XGBoost/LSTM) é executado em modo *Serverless*. O custo é zero enquanto não houver requisições.
5.  **Frontend:** **Vercel** conectado ao repositório GitHub.

**Prós:** Custo zero, ferramentas de alta visibilidade (Hugging Face), escalabilidade automática.  
**Contras:** Dependência de múltiplos provedores (SaaS).

---

## 3. Opção 2: Arquitetura "Modern Data Stack" (Alta Performance)
*Foco em velocidade de processamento (OLAP) e ferramentas modernas de engenharia de dados.*

### Fluxo de Dados:
1.  **Ingestão (ETL):** **Railway Worker**. Um container dedicado executa o processamento utilizando **DuckDB**. O DuckDB permite realizar JOINs e agregações de milhões de linhas diretamente dos ZIPs em segundos.
2.  **Hospedagem de Arquivos (Bronze/Silver):** **Cloudflare R2**. Object Storage compatível com S3, porém **sem taxas de transferência (egress)**. Ideal para fluxos intensos de treino de modelos.
3.  **Banco de Dados (Gold):** **Neon.tech**. PostgreSQL Serverless com suporte a *Branching* de banco de dados (permite criar clones do banco para testes em 1 segundo).
4.  **Hospedagem da API:** **Railway.app**. Plataforma PaaS de alta produtividade. Deployment automático via `git push`.
5.  **Frontend:** **Vercel**.

**Prós:** Performance extrema (DuckDB), facilidade de desenvolvimento, ferramentas integradas.  
**Contras:** Pode gerar pequenos custos (aprox. $5/mês) se o volume de dados ultrapassar o free tier.

---

## 4. Opção 3: Arquitetura "Total Control" (VPS & Docker Centralizado)
*Foco em controle total da infraestrutura, soberania de dados e aprendizado de SysAdmin.*

### Fluxo de Dados:
1.  **Infraestrutura:** Uma única **VPS (Virtual Private Server)** rodando Ubuntu (DigitalOcean, Hetzner ou AWS EC2).
2.  **Ingestão & ETL:** **Dockerized Cron Jobs**. Scripts Python rodam em containers agendados na própria VPS, baixando os dados e salvando-os no sistema de arquivos local da máquina.
3.  **Hospedagem de Arquivos:** **Volume Docker Local**. Os dados Parquet e CSVs brutos moram no disco rígido da VPS.
4.  **Banco de Dados:** **PostGIS em Docker**. Uma instância gerenciada manualmente dentro da VPS. Você controla a memória, buffers e acessos.
5.  **Hospedagem da API:** Container Docker na mesma rede interna da VPS, exposto via **Nginx** (Proxy Reverso) com certificado SSL via **Let's Encrypt**.

**Prós:** Controle total, menor latência entre banco e API, custo fixo e previsível.  
**Contras:** Exige manutenção manual (backups, atualizações de segurança, configuração de firewall).

---

## 5. Comparativo Técnico para Decisão

| Recurso | **Opção 1 (Custo Zero)** | **Opção 2 (Performance)** | **Opção 3 (VPS)** |
| :--- | :--- | :--- | :--- |
| **Custo Estimado** | R$ 0,00 | R$ 25 - 50 /mês | R$ 30,00 (Fixo) |
| **Manutenção** | Mínima (SaaS) | Média (PaaS) | Alta (Auto-gerenciado) |
| **Velocidade ETL** | Média | **Altíssima (DuckDB)** | Alta |
| **Complexidade Setup** | Baixa | Baixa | Alta |
| **Uso de Docker** | Essencial (Cloud Run) | Essencial (Railway) | **Crítico (Orquestração)** |

---

## 6. Recomendação do Autor
Para o escopo do TCC2, a **Opção 1** é recomendada pela viabilidade financeira e pelo uso de tecnologias que enriquecem o currículo acadêmico (Supabase, Google Cloud Run, Hugging Face). 

Caso o volume de dados do INMET (histórico completo de todas as estações do Brasil) torne o processamento lento no GitHub Actions, a migração pontual para a estratégia de processamento da **Opção 2 (DuckDB)** é o caminho natural de evolução.

---
*Este documento visa subsidiar a decisão estratégica de infraestrutura para o TCC2.*
