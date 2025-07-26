import requests
from bs4 import BeautifulSoup
import json

url = "https://statusinvest.com.br/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html",
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

def extrair_lista_por_titulo(titulo_h3):
    """Extrai lista de ativos abaixo do <h3> com texto 'titulo_h3'"""
    secao = soup.find("h3", string=titulo_h3)
    resultados = []
    if not secao:
        return resultados
    lista_div = secao.find_next("div", {"role": "list"})
    if not lista_div:
        return resultados

    itens = lista_div.find_all("div", {"role": "listitem"})
    for item in itens:
        ticker_tag = item.find("h4")
        variacao_tag = item.find("span", {"class": "value"})
        preco_tag = item.find("span", {"class": "other-value"})

        ticker = ticker_tag.contents[0].strip() if ticker_tag else ""
        empresa = ticker_tag.find("small").text.strip() if ticker_tag and ticker_tag.find("small") else ""
        
        variacao = ""
        if variacao_tag:
            i_tag = variacao_tag.find("i")
            if i_tag:
                i_tag.extract()
            variacao = variacao_tag.get_text(strip=True)

        preco = preco_tag.get_text(strip=True) if preco_tag else ""

        resultados.append({
            "ticker": ticker,
            "empresa": empresa,
            "variacao": variacao,
            "preco": preco
        })
    return resultados

# Cotacoes de hoje: ALTAS, BAIXAS, DIVIDENDOS
cotacoes_hoje = {
    "altas": extrair_lista_por_titulo("ALTAS"),
    "baixas": extrair_lista_por_titulo("BAIXAS"),
    "dividendos": extrair_lista_por_titulo("DIVIDENDOS"),
}

# Ranking de Ações
ranking = {}

# A div com class 'cards d-flex flex-wrap ' tem as 4 categorias em divs internas
cards_div = soup.find("h2", string=lambda t: t and "Ranking de Ações" in t)
if cards_div:
    container = cards_div.find_next_sibling("div", class_="cards d-flex flex-wrap ")
    if container:
        categorias = container.find_all("div", class_="itens-4")
        nomes_categorias = [
            "mais_populares",
            "maiores_lucros",
            "maiores_roes",
            "liquidez_media_diaria"
        ]
        for idx, cat_div in enumerate(categorias):
            categoria_nome = nomes_categorias[idx]
            ativos = []
            # Cada ativo está num div com role listitem dentro do div categoria
            lista_ativos = cat_div.find_all("div", role="listitem")
            for ativo in lista_ativos:
                ticker_tag = ativo.find("h4")
                if not ticker_tag:
                    continue
                ticker = ticker_tag.contents[0].strip()
                empresa = ticker_tag.find("small").text.strip() if ticker_tag.find("small") else ""

                preco_tag = ativo.find("span", class_="other-value")
                preco = preco_tag.get_text(strip=True) if preco_tag else ""

                variacao_tag = ativo.find("span", class_="value")
                variacao = ""
                if variacao_tag:
                    i_tag = variacao_tag.find("i")
                    if i_tag:
                        i_tag.extract()
                    variacao = variacao_tag.get_text(strip=True)

                ativos.append({
                    "ticker": ticker,
                    "empresa": empresa,
                    "variacao": variacao,
                    "preco": preco
                })
            ranking[categoria_nome] = ativos

resultado_final = {
    "cotacoes_hoje": cotacoes_hoje,
    "ranking_acoes": ranking
}

# Salvar JSON
with open("fundos-imobiliarios.json", "w", encoding="utf-8") as f:
    json.dump(resultado_final, f, ensure_ascii=False, indent=2)

print(f"✅ Dados coletados e salvos com sucesso!")
