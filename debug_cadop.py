import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE_DIR, "data", "cadastro_operadoras_ativas.csv")

print("Arquivo:", PATH)

with open(PATH, "r", encoding="latin-1", errors="ignore", newline="") as f:
    sample = f.read(8000)

best = ";"
for d in [";", ",", "\t", "|"]:
    if sample.count(d) > sample.count(best):
        best = d

print("Delimitador provavel:", repr(best))

with open(PATH, "r", encoding="latin-1", errors="ignore", newline="") as f:
    r = csv.reader(f, delimiter=best)
    header = next(r, [])
    print("Header (colunas):")
    for i, col in enumerate(header):
        print(i, ":", col)
    print("\nPrimeira linha (amostra):")
    row = next(r, [])
    print(row)
