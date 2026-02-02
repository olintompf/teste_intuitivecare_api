import os
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Teste Intuitive API", version="1.0")


# =========================
# CONEXAO COM O BANCO
# =========================
def get_db_conn():
    host = os.getenv("PGHOST", "127.0.0.1").strip()
    port = os.getenv("PGPORT", "5432").strip()
    dbname = os.getenv("PGDATABASE", "teste_intuitive").strip()
    user = os.getenv("PGUSER", "postgres").strip()
    password = os.getenv("PGPASSWORD", "").strip()

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        options="-c client_encoding=UTF8",
    )


# =========================
# HELPERS
# =========================
def fetch_all(sql: str, params: tuple = ()):
    with get_db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_one(sql: str, params: tuple = ()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


# =========================
# ENDPOINTS
# =========================
@app.get("/api/operadoras")
def list_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=200),
    q: Optional[str] = None,
):
    offset = (page - 1) * limit

    where = ""
    params = []

    if q and q.strip():
        qq = q.strip()
        where = "WHERE cnpj ILIKE %s OR razao_social ILIKE %s"
        params.extend([f"%{qq}%", f"%{qq}%"])

    total_row = fetch_one(
        f"SELECT COUNT(*) AS total FROM operadoras {where}",
        tuple(params),
    )
    total = int(total_row["total"]) if total_row else 0

    rows = fetch_all(
        f"""
        SELECT cnpj, registro_ans, razao_social, modalidade, uf
        FROM operadoras
        {where}
        ORDER BY razao_social ASC NULLS LAST
        LIMIT %s OFFSET %s
        """,
        tuple(params + [limit, offset]),
    )

    return {
        "data": rows,
        "page": page,
        "limit": limit,
        "total": total,
    }


@app.get("/api/operadoras/{cnpj}")
def get_operadora(cnpj: str):
    cnpj = "".join(ch for ch in cnpj if ch.isdigit())
    if not cnpj:
        raise HTTPException(status_code=400, detail="cnpj invalido")

    row = fetch_one(
        """
        SELECT cnpj, registro_ans, razao_social, modalidade, uf
        FROM operadoras
        WHERE cnpj = %s
        """,
        (cnpj,),
    )

    if not row:
        raise HTTPException(status_code=404, detail="operadora nao encontrada")

    return row


@app.get("/api/operadoras/{cnpj}/despesas")
def get_despesas_operadora(cnpj: str):
    cnpj = "".join(ch for ch in cnpj if ch.isdigit())
    if not cnpj:
        raise HTTPException(status_code=400, detail="cnpj invalido")

    rows = fetch_all(
        """
        SELECT ano, trimestre, SUM(valor_despesas) AS total_despesas
        FROM despesas_consolidadas
        WHERE cnpj = %s
        GROUP BY ano, trimestre
        ORDER BY ano ASC, trimestre ASC
        """,
        (cnpj,),
    )

    return {"cnpj": cnpj, "historico": rows}


@app.get("/api/estatisticas")
def get_estatisticas():
    total_row = fetch_one(
        "SELECT SUM(valor_despesas) AS total FROM despesas_consolidadas"
    )
    total = float(total_row["total"]) if total_row and total_row["total"] else 0.0

    media_row = fetch_one(
        "SELECT AVG(valor_despesas) AS media FROM despesas_consolidadas"
    )
    media = float(media_row["media"]) if media_row and media_row["media"] else 0.0

    top5 = fetch_all(
        """
        SELECT
            d.cnpj,
            MAX(o.razao_social) AS razao_social,
            MAX(o.uf) AS uf,
            SUM(d.valor_despesas) AS total_despesas
        FROM despesas_consolidadas d
        JOIN operadoras o ON o.cnpj = d.cnpj
        GROUP BY d.cnpj
        ORDER BY total_despesas DESC
        LIMIT 5
        """
    )

    por_uf = fetch_all(
        """
        SELECT o.uf, SUM(d.valor_despesas) AS total_despesas
        FROM despesas_consolidadas d
        JOIN operadoras o ON o.cnpj = d.cnpj
        WHERE o.uf IS NOT NULL AND o.uf <> ''
        GROUP BY o.uf
        ORDER BY total_despesas DESC
        LIMIT 10
        """
    )

    return {
        "total_despesas": total,
        "media_despesas": media,
        "top5_operadoras": top5,
        "top_ufs": por_uf,
    }
