import requests
from bs4 import BeautifulSoup
import json

# URL e headers para simular navegador
url = "https://statusinvest.com.br/acoes"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)","Accept": "text/html",}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

def extrair_lista_por_titulo(titulo_h3):
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

def extrair_ranking_acoes():
    categorias = [
        "MAIS POPULARES",
        "MAIORES LUCROS",
        "MAIORES ROES",
        "LIQUIDEZ MÉDIA DIÁRIA"
    ]
    resultados = {}
    h2 = soup.find("h2", string=lambda t: t and "Ranking de A" in t)
    if not h2:
        return resultados
    container = h2.find_next("div", class_="cards d-flex flex-wrap ")
    if not container:
        return resultados
    blocos = container.find_all("div", class_="itens-4")
    for idx, bloco in enumerate(blocos):
        nome_categoria = categorias[idx] if idx < len(categorias) else f"Categoria {idx+1}"
        ativos = []
        itens = bloco.find_all("div", {"role": "listitem"})
        for item in itens:
            ticker_tag = item.find("h4")
            if not ticker_tag:
                continue
            ticker = ticker_tag.contents[0].strip()
            empresa = ticker_tag.find("small").text.strip() if ticker_tag.find("small") else ""
            preco_tag = item.find("span", class_="other-value")
            preco = preco_tag.get_text(strip=True) if preco_tag else ""
            variacao_tag = item.find("span", class_="value")
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
        resultados[nome_categoria] = ativos
    return resultados

# Estrutura base
dados = {
    "ranking_acoes": {"cotacoes_hoje": {}, "ranking": {}},
    "ranking_fiis": {"cotacoes_hoje": {}, "ranking": {}},
    "ranking_bdrs": {"cotacoes_hoje": {}, "ranking": {}},
}

# Coleta ALTAS, BAIXAS, DIVIDENDOS
for tipo in ["ALTAS", "BAIXAS", "DIVIDENDOS"]:
    lista = extrair_lista_por_titulo(tipo)
    for item in lista:
        ticker = item["ticker"]
        if ticker.endswith("11"):
            dados["ranking_fiis"]["cotacoes_hoje"].setdefault(tipo.lower(), []).append(item)
        elif ticker.endswith("34"):
            dados["ranking_bdrs"]["cotacoes_hoje"].setdefault(tipo.lower(), []).append(item)
        else:
            dados["ranking_acoes"]["cotacoes_hoje"].setdefault(tipo.lower(), []).append(item)

# Ranking de ações
dados["ranking_acoes"]["ranking"] = extrair_ranking_acoes()

# Salvar em JSON
arquivo = "statusinvest_dados.json"
with open(arquivo, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print(f"✅ Dados coletados e salvos com sucesso em {arquivo}")
