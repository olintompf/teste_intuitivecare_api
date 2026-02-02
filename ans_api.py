import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"

def listar_pastas():
    response = requests.get(BASE_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pastas = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href and href.endswith("/"):
            if href != "../":
                pastas.append(href.replace("/", ""))

    return pastas
