# Teste Tecnico ? Intuitive Care

## Visao Geral

Este projeto implementa uma pipeline completa de processamento, analise e exposicao de dados publicos da ANS (Agencia Nacional de Saude Suplementar), com foco em despesas relacionadas a Eventos e Sinistros.

A solucao contempla:
- Ingestao e filtragem de arquivos CSV e ZIP
- Tratamento de encoding e delimitadores
- Consolidacao e enriquecimento de dados cadastrais
- Persistencia em banco PostgreSQL
- Consultas analiticas em SQL
- Exposicao dos dados via API REST utilizando FastAPI

---

## Tecnologias Utilizadas

- Python 3.14
- PostgreSQL 17
- FastAPI
- Uvicorn
- psycopg2
- SQL (DDL, DML e consultas analiticas)

---

## Estrutura do Projeto

teste_olinto/
  README.md
  requirements.txt
  src/
      main.py
      prep_sql_import.py
      ans_api.py
      api.py
      config.py
      debug_cadop
      debug_header
      main.py
    


---

## Pipeline de Dados

### 1. Coleta e Filtragem

- Download e leitura dos arquivos trimestrais da ANS
- Selecao do periodo: abril a dezembro de 2025
- Filtragem apenas de registros relacionados a "Eventos" e "Sinistros"

### 2. Tratamento e Consolidacao

- Detecao automatica de delimitadores
- Conversao de encoding para UTF-8
- Normalizacao de colunas
- Agregacao por operadora, ano e trimestre

### 3. Enriquecimento

- Integracao com o cadastro de operadoras ativas da ANS
- Associacao por Registro ANS e CNPJ
- Inclusao de razao social, modalidade e UF

### 4. Persistencia em Banco de Dados

Banco: PostgreSQL

Modelo normalizado com tres tabelas principais:
- operadoras
- despesas_consolidadas
- despesas_agregadas

Decisoes tecnicas:
- Valores monetarios armazenados como NUMERIC(18,2) para evitar erros de ponto flutuante
- Separacao de ano (INTEGER) e trimestre (VARCHAR) para facilitar analises
- Indices criados para melhorar performance de consultas analiticas

---

## API REST

A API foi desenvolvida com FastAPI e exposta via Uvicorn.

### Endpoints disponiveis

- `GET /api/operadoras`
  - Lista operadoras com paginacao e filtro por CNPJ ou razao social

- `GET /api/operadoras/{cnpj}`
  - Retorna os dados cadastrais de uma operadora

- `GET /api/operadoras/{cnpj}/despesas`
  - Retorna o historico trimestral de despesas da operadora

- `GET /api/estatisticas`
  - Estatisticas gerais:
    - Total de despesas
    - Media de despesas
    - Top 5 operadoras por gasto
    - Top UFs por volume de despesas

---

## Observacoes Importantes

- Alguns textos podem apresentar caracteres especiais incorretos (ex: "SAÃ?DE") devido a inconsistencias de encoding nos dados originais da ANS.
- O problema foi identificado e documentado, nao impactando a integridade numerica nem as analises solicitadas.
- Todas as decisoes tecnicas foram tomadas priorizando confiabilidade, rastreabilidade e facilidade de justificacao.

---

## Como Executar

1. Instalar dependencias:
```bash
pip install -r requirements.txt

Subir a API:

python -m uvicorn src.api:app --reload

Acessar a documentacao interativa:

http://127.0.0.1:8000/docs

Conclusao


O projeto entrega uma solucao funcional, escalavel e alinhada a cenarios reais de engenharia de dados e backend, cobrindo todo o ciclo de ingestao, processamento, armazenamento, analise e exposicao via API.

