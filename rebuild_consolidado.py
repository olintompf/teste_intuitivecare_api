import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IN_DIR = os.path.join(BASE_DIR, "output", "Despesas_Eventos_Sinistros")
CADOP = os.path.join(BASE_DIR, "data", "cadastro_operadoras_ativas.csv")

OUT_CONS = os.path.join(BASE_DIR, "output", "consolidado_despesas.csv")
OUT_ENR = os.path.join(BASE_DIR, "output", "consolidado_despesas_enriquecido.csv")

FILES = [
    ("2T", "2025", os.path.join(IN_DIR, "2T2025.csv")),
    ("3T", "2025", os.path.join(IN_DIR, "3T2025.csv")),
]

def sniff_delim(path):
    with open(path, "r", encoding="latin-1", errors="ignore") as f:
        sample = f.read(8000)
    best = ";"
    for d in [";", ",", "\t", "|"]:
        if sample.count(d) > sample.count(best):
            best = d
    return best

def norm_text(s):
    if s is None:
        return ""
    return str(s).strip()

def only_digits(s):
    return "".join(ch for ch in norm_text(s) if ch.isdigit())

def norm_cnpj(s):
    d = only_digits(s)
    return d.zfill(14) if d else ""

def norm_money_to_float(s):
    t = norm_text(s)
    if not t:
        return 0.0
    t = t.replace(" ", "")
    if t.count(",") == 1 and t.count(".") >= 1:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(",") == 1 and t.count(".") == 0:
        t = t.replace(",", ".")
    try:
        return float(t)
    except Exception:
        return 0.0

def match_eventos_sinistros(desc):
    d = norm_text(desc).lower()
    return ("eventos" in d) or ("sinistros" in d)

def lower_list(cols):
    return [norm_text(x).lower() for x in cols]

def idx(header_lower, names):
    for n in names:
        n = n.lower()
        if n in header_lower:
            return header_lower.index(n)
    return None

def load_cadop_map():
    if not os.path.exists(CADOP):
        print("CADOP nao encontrado:", CADOP)
        return {}

    d = sniff_delim(CADOP)
    m = {}

    with open(CADOP, "r", encoding="latin-1", errors="ignore", newline="") as f:
        r = csv.reader(f, delimiter=d)
        header = next(r, [])
        hl = lower_list(header)

        # Real header fields (from your debug):
        # REGISTRO_OPERADORA, CNPJ, Razao_Social, Modalidade, UF ...
        i_reg = idx(hl, ["registro_operadora", "registro", "registro_ans", "registro ans"])
        i_cnpj = idx(hl, ["cnpj"])
        i_razao = idx(hl, ["razao_social", "razao social", "razao_social", "razao"])
        i_mod = idx(hl, ["modalidade"])
        i_uf = idx(hl, ["uf"])

        if i_reg is None:
            print("ERRO: nao achei coluna de registro no CADOP.")
            print("Header:", header)
            return {}

        for row in r:
            if not row:
                continue

            reg_raw = row[i_reg] if i_reg < len(row) else ""
            reg = only_digits(reg_raw)
            if not reg:
                continue

            cnpj = norm_cnpj(row[i_cnpj]) if i_cnpj is not None and i_cnpj < len(row) else ""
            razao = norm_text(row[i_razao]) if i_razao is not None and i_razao < len(row) else ""
            mod = norm_text(row[i_mod]) if i_mod is not None and i_mod < len(row) else ""
            uf = norm_text(row[i_uf]).upper() if i_uf is not None and i_uf < len(row) else ""

            m[reg] = {
                "cnpj": cnpj,
                "razao": razao,
                "modalidade": mod,
                "uf": uf,
            }

    return m

cad_map = load_cadop_map()
print("Cadastros carregados:", len(cad_map))

# Aggregate by (registro_operadora, ano, trimestre)
agg = {}
total_rows = 0
kept_rows = 0

for tri, ano, path in FILES:
    if not os.path.exists(path):
        print("Arquivo nao encontrado:", path)
        continue

    delim = sniff_delim(path)
    print("Lendo:", os.path.basename(path), "delim:", repr(delim))

    with open(path, "r", encoding="latin-1", errors="ignore", newline="") as f:
        r = csv.reader(f, delimiter=delim)
        for row in r:
            total_rows += 1
            if not row or len(row) < 5:
                continue

            # No header, by position:
            # 0 data, 1 registro, 2 codigo, 3 descricao, 4 valor1, 5 valor2 (sometimes)
            reg = only_digits(row[1]) if len(row) > 1 else ""
            desc = row[3] if len(row) > 3 else ""
            if not reg:
                continue
            if not match_eventos_sinistros(desc):
                continue

            val = norm_money_to_float(row[5]) if len(row) > 5 else norm_money_to_float(row[4])

            key = (reg, int(ano), tri)
            agg[key] = agg.get(key, 0.0) + val
            kept_rows += 1

print("Total linhas lidas:", total_rows)
print("Linhas mantidas (eventos/sinistros):", kept_rows)
print("Grupos agregados:", len(agg))

# Write consolidado_despesas.csv WITH RegistroANS extra column
with open(OUT_CONS, "w", encoding="utf-8", newline="") as fout:
    w = csv.writer(fout, delimiter=";")
    w.writerow(["RegistroANS", "CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"])

    written = 0
    sem_match = 0

    for (reg, ano, tri), total in sorted(agg.items()):
        info = cad_map.get(reg)
        if info:
            cnpj = info["cnpj"]
            razao = info["razao"]
        else:
            sem_match += 1
            cnpj = ""
            razao = ""

        w.writerow([reg, cnpj, razao, tri, ano, f"{total:.2f}"])
        written += 1

print("OK consolidado_despesas.csv escrito:", written, "sem_match:", sem_match)
print("Arquivo:", OUT_CONS)

# Write enriched version (add Modalidade, UF)
with open(OUT_ENR, "w", encoding="utf-8", newline="") as fout:
    w = csv.writer(fout, delimiter=";")
    w.writerow(["RegistroANS", "CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas", "Modalidade", "UF"])

    written = 0
    sem_match = 0

    for (reg, ano, tri), total in sorted(agg.items()):
        info = cad_map.get(reg)
        if info:
            cnpj = info["cnpj"]
            razao = info["razao"]
            mod = info["modalidade"]
            uf = info["uf"]
        else:
            sem_match += 1
            cnpj = ""
            razao = ""
            mod = "SEM_MATCH"
            uf = "SEM_MATCH"

        w.writerow([reg, cnpj, razao, tri, ano, f"{total:.2f}", mod, uf])
        written += 1

print("OK consolidado_despesas_enriquecido.csv escrito:", written, "sem_match:", sem_match)
print("Arquivo:", OUT_ENR)
