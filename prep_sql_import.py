import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

CADOP_IN = os.path.join(DATA_DIR, "cadastro_operadoras_ativas.csv")
DESP_IN = os.path.join(OUTPUT_DIR, "consolidado_despesas_enriquecido.csv")
AGG_IN = os.path.join(OUTPUT_DIR, "despesas_agregadas.csv")

SQL_DIR = os.path.join(OUTPUT_DIR, "sql_import")
os.makedirs(SQL_DIR, exist_ok=True)

CADOP_OUT = os.path.join(SQL_DIR, "operadoras_sql.csv")
DESP_OUT = os.path.join(SQL_DIR, "despesas_consolidadas_sql.csv")
AGG_OUT = os.path.join(SQL_DIR, "despesas_agregadas_sql.csv")

def sniff_delim(path, encoding):
    with open(path, "r", encoding=encoding, errors="ignore") as f:
        sample = f.read(5000)
    best = ";"
    for d in [";", ",", "\t", "|"]:
        if sample.count(d) > sample.count(best):
            best = d
    return best

def norm_cnpj(s):
    if s is None:
        return ""
    digits = "".join(ch for ch in str(s) if ch.isdigit())
    return digits.zfill(14) if digits else ""

def norm_text(s):
    if s is None:
        return ""
    return str(s).strip()

def norm_uf(s):
    t = norm_text(s).upper()
    if len(t) == 2:
        return t
    return ""

def norm_money(s):
    if s is None:
        return ""
    t = str(s).strip()
    if not t:
        return ""
    t = t.replace(" ", "")
    if t.count(",") == 1 and t.count(".") >= 1:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(",") == 1 and t.count(".") == 0:
        t = t.replace(",", ".")
    return t

def index_header(header):
    m = {}
    for i, col in enumerate(header):
        key = norm_text(col).lower()
        m[key] = i
    return m

print("BASE_DIR:", BASE_DIR)
print("SQL_DIR:", SQL_DIR)

# -------------------------
# 1) operadoras_sql.csv
# -------------------------
print("\n[1/3] Building:", CADOP_OUT)
cadop_delim = sniff_delim(CADOP_IN, "latin-1")
with open(CADOP_IN, "r", encoding="latin-1", errors="ignore", newline="") as fin, \
     open(CADOP_OUT, "w", encoding="utf-8", newline="") as fout:
    reader = csv.reader(fin, delimiter=cadop_delim)
    writer = csv.writer(fout, delimiter=",")

    header = next(reader, [])
    hm = index_header(header)

    def find_col(possible):
        for name in possible:
            k = name.lower()
            if k in hm:
                return hm[k]
        return None

    idx_reg = find_col(["registro ans", "registro_ans", "registro"])
    idx_cnpj = find_col(["cnpj"])
    idx_razao = find_col(["razao social", "razao_social"])
    idx_mod = find_col(["modalidade"])
    idx_uf = find_col(["uf"])

    writer.writerow(["cnpj", "registro_ans", "razao_social", "modalidade", "uf"])

    rows = 0
    for row in reader:
        if not row:
            continue
        reg = row[idx_reg] if idx_reg is not None and idx_reg < len(row) else ""
        cnpj = row[idx_cnpj] if idx_cnpj is not None and idx_cnpj < len(row) else ""
        razao = row[idx_razao] if idx_razao is not None and idx_razao < len(row) else ""
        mod = row[idx_mod] if idx_mod is not None and idx_mod < len(row) else ""
        uf = row[idx_uf] if idx_uf is not None and idx_uf < len(row) else ""

        writer.writerow([norm_cnpj(cnpj), norm_text(reg), norm_text(razao), norm_text(mod), norm_uf(uf)])
        rows += 1

print("OK rows:", rows)

# -------------------------
# 2) despesas_consolidadas_sql.csv
# -------------------------
print("\n[2/3] Building:", DESP_OUT)
desp_delim = sniff_delim(DESP_IN, "utf-8")
with open(DESP_IN, "r", encoding="utf-8", errors="ignore", newline="") as fin, \
     open(DESP_OUT, "w", encoding="utf-8", newline="") as fout:
    reader = csv.reader(fin, delimiter=desp_delim)
    writer = csv.writer(fout, delimiter=",")

    header = next(reader, [])
    hm = index_header(header)

    def find_col2(possible):
        for name in possible:
            k = name.lower()
            if k in hm:
                return hm[k]
        return None

    idx_cnpj = find_col2(["cnpj"])
    idx_razao = find_col2(["razaosocial", "razao_social", "razao social"])
    idx_tri = find_col2(["trimestre"])
    idx_ano = find_col2(["ano"])
    idx_val = find_col2(["valordespesas", "valor_despesas", "valor despesas", "valordespesa"])

    writer.writerow(["cnpj", "razao_social", "trimestre", "ano", "valor_despesas"])

    rows = 0
    for row in reader:
        if not row:
            continue
        cnpj = row[idx_cnpj] if idx_cnpj is not None and idx_cnpj < len(row) else ""
        razao = row[idx_razao] if idx_razao is not None and idx_razao < len(row) else ""
        tri = row[idx_tri] if idx_tri is not None and idx_tri < len(row) else ""
        ano = row[idx_ano] if idx_ano is not None and idx_ano < len(row) else ""
        val = row[idx_val] if idx_val is not None and idx_val < len(row) else ""

        writer.writerow([norm_cnpj(cnpj), norm_text(razao), norm_text(tri), norm_text(ano), norm_money(val)])
        rows += 1

print("OK rows:", rows)

# -------------------------
# 3) despesas_agregadas_sql.csv
# -------------------------
print("\n[3/3] Building:", AGG_OUT)
agg_delim = sniff_delim(AGG_IN, "utf-8")
with open(AGG_IN, "r", encoding="utf-8", errors="ignore", newline="") as fin, \
     open(AGG_OUT, "w", encoding="utf-8", newline="") as fout:
    reader = csv.reader(fin, delimiter=agg_delim)
    writer = csv.writer(fout, delimiter=",")

    header = next(reader, [])
    hm = index_header(header)

    def find_col3(possible):
        for name in possible:
            k = name.lower()
            if k in hm:
                return hm[k]
        return None

    idx_razao = find_col3(["razaosocial", "razao_social", "razao social"])
    idx_uf = find_col3(["uf"])
    idx_ano = find_col3(["ano"])
    idx_tri = find_col3(["trimestre"])
    idx_total = find_col3(["total_despesas", "totaldespesas", "total"])
    idx_media = find_col3(["media_despesas", "mediadespesas", "media"])
    idx_std = find_col3(["desvio_padrao", "desviopadrao", "desvio", "std", "stdev"])

    writer.writerow(["razao_social", "uf", "ano", "trimestre", "total_despesas", "media_despesas", "desvio_padrao"])

    rows = 0
    for row in reader:
        if not row:
            continue
        razao = row[idx_razao] if idx_razao is not None and idx_razao < len(row) else ""
        uf = row[idx_uf] if idx_uf is not None and idx_uf < len(row) else ""
        ano = row[idx_ano] if idx_ano is not None and idx_ano < len(row) else ""
        tri = row[idx_tri] if idx_tri is not None and idx_tri < len(row) else ""
        total = row[idx_total] if idx_total is not None and idx_total < len(row) else ""
        media = row[idx_media] if idx_media is not None and idx_media < len(row) else ""
        std = row[idx_std] if idx_std is not None and idx_std < len(row) else ""

        writer.writerow([norm_text(razao), norm_uf(uf), norm_text(ano), norm_text(tri),
                         norm_money(total), norm_money(media), norm_money(std)])
        rows += 1

print("OK rows:", rows)

print("\nDONE. Files created in:", SQL_DIR)
print(" -", CADOP_OUT)
print(" -", DESP_OUT)
print(" -", AGG_OUT)
