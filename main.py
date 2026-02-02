import os
import csv
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(
    BASE_DIR,
    "output",
    "consolidado_despesas_enriquecido.csv"
)

OUTPUT_CSV = os.path.join(
    BASE_DIR,
    "output",
    "despesas_agregadas.csv"
)

print("Entrada:", INPUT_CSV)
print("Saida:", OUTPUT_CSV)

grupos = {}

linhas_lidas = 0

with open(INPUT_CSV, "r", encoding="latin-1", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        linhas_lidas += 1

        ano = row.get("Ano", "").strip()
        trimestre = row.get("Trimestre", "").strip()

        if not ano or not trimestre:
            continue

        valor_str = row.get("ValorDespesas", "").replace(",", ".")
        try:
            valor = float(valor_str)
        except Exception:
            continue

        chave = (ano, trimestre)
        grupos.setdefault(chave, []).append(valor)

print("Linhas lidas:", linhas_lidas)
print("Grupos formados:", len(grupos))

resultados = []

for (ano, trimestre), valores in grupos.items():
    total = sum(valores)
    media = total / len(valores)

    if len(valores) > 1:
        variancia = sum((v - media) ** 2 for v in valores) / len(valores)
        desvio = math.sqrt(variancia)
    else:
        desvio = 0.0

    resultados.append({
        "Ano": ano,
        "Trimestre": trimestre,
        "TotalDespesas": round(total, 2),
        "MediaDespesas": round(media, 2),
        "DesvioPadrao": round(desvio, 2)
    })

# ordenar por ano + trimestre
resultados.sort(key=lambda x: (x["Ano"], x["Trimestre"]))

with open(OUTPUT_CSV, "w", encoding="latin-1", newline="") as f:
    fieldnames = [
        "Ano",
        "Trimestre",
        "TotalDespesas",
        "MediaDespesas",
        "DesvioPadrao"
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    for row in resultados:
        writer.writerow(row)

print("OK: despesas_agregadas.csv gerado por Ano e Trimestre.")
