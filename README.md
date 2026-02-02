# Teste Tecnico - Intuitive Care

## Visao geral
Pipeline completa para coletar, tratar, consolidar e expor dados publicos da ANS, com foco em despesas relacionadas a "Eventos" e "Sinistros".

Entrega:
- Pipeline (Python) para preparar os arquivos
- Persistencia em PostgreSQL (tabelas + carga)
- Consultas analiticas (SQL)
- API REST (FastAPI) com Swagger

---

## Tecnologias
- Python 3.x
- PostgreSQL
- FastAPI + Uvicorn
- psycopg2
- SQL

---

## Estrutura do projeto (principais arquivos)
teste_olinto/
README.md
requirements.txt
src/
api.py
config.py
ans_api.py
main.py
prep_sql_import.py
rebuild_consolidado.py
debug_header.py
debug_cadop.py
output/
data/


---

## Banco de dados (modelo)
Tabelas:
- operadoras
- despesas_consolidadas
- despesas_agregadas

Decisoes:
- valores monetarios: NUMERIC(18,2) para precisao
- periodo: ano (INTEGER) e trimestre (VARCHAR)
- indices para performance

---

## API (endpoints)
- GET /api/operadoras
- GET /api/operadoras/{cnpj}
- GET /api/operadoras/{cnpj}/despesas
- GET /api/estatisticas

Swagger:
- http://127.0.0.1:8000/docs

---

## Observacoes (encoding)
Alguns textos podem apresentar caracteres incorretos (ex: "SAÃ?DE") devido ao encoding original das bases da ANS.
Isso nao afeta a integridade numerica nem as analises.

---

## Como executar (avaliador)

### 1) Clonar e instalar dependencias
```bash
git clone https://github.com/olintompf/teste_intuitivecare_api.git
cd teste_intuitivecare_api
pip install -r requirements.txt
2) Configurar PostgreSQL
Crie um banco:

teste_intuitive

Defina variaveis de ambiente (Windows CMD):

setx PGHOST "127.0.0.1"
setx PGPORT "5432"
setx PGDATABASE "teste_intuitive"
setx PGUSER "postgres"
setx PGPASSWORD "SUA_SENHA_AQUI"
Feche e abra o terminal novamente (para o setx valer).

3) Subir a API
Na raiz do projeto:

python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
Acesse:

http://127.0.0.1:8000/docs

