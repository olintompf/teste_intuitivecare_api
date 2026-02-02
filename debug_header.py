import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "output", "consolidado_despesas_enriquecido.csv")

print("Arquivo:", INPUT_CSV)

with open(INPUT_CSV, "r", encoding="utf-8", errors="ignore", newline="") as f:
    sample = f.read(8000)

best = ";"
for d in [";", ",", "\t", "|"]:
    if sample.count(d) > sample.count(best):
        best = d

print("Delimitador provavel:", repr(best))

with open(INPUT_CSV, "r", encoding="utf-8", errors="ignore", newline="") as f:
    reader = csv.reader(f, delimiter=best)
    header = next(reader, [])
    print("Header colunas (index: nome):")
    for i, col in enumerate(header):
        print(i, ":", col)
    print("\nPrimeira linha (amostra):")
    row = next(reader, [])
    print(row)
