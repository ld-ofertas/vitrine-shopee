import os
import time
import hashlib
import json
import requests

APP_ID = os.getenv("SHOPEE_APP_ID", "").strip()
APP_SECRET = os.getenv("SHOPEE_APP_SECRET", "").strip()

# Categorias e as palavras-chave para busca na Shopee
CATEGORIAS = {
    "Eletrônicos": "eletronicos",
    "Casa": "casa decoracao",
    "Moda": "moda masculina feminina",
    "Beleza": "maquiagem skincare"
}

def fetch_category_products(keyword, limit=6):
    """Busca produtos na Shopee baseados em uma palavra-chave"""
    if not APP_ID or not APP_SECRET:
        return []

    timestamp = int(time.time())
    query = f"""
    query {{
      productOfferV2(keyword: "{keyword}", page: 1, limit: {limit}) {{
        nodes {{
          productName
          price
          imageUrl
          offerLink
        }}
      }}
    }}
    """
    
    payload = json.dumps({"query": query})
    factor = f"{APP_ID}{timestamp}{payload}{APP_SECRET}"
    signature = hashlib.sha256(factor.encode('utf-8')).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={APP_ID}, Timestamp={timestamp}, Signature={signature}'
    }

    url = "https://open-api.affiliate.shopee.com.br/graphql"
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        res_data = response.json()
        nodes = res_data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
        
        produtos = []
        for item in nodes:
            price_val = float(item.get('price', 0))
            produtos.append({
                "title": item.get("productName", "Produto Shopee"),
                "price": f"R$ {price_val:.2f}".replace(".", ","),
                "image": item.get("imageUrl", "https://via.placeholder.com/250"),
                "link": item.get("offerLink", "#")
            })
        return produtos
    except Exception as e:
        print(f"Erro ao buscar palavra-chave '{keyword}': {e}")
        return []

def get_all_products():
    todos_produtos = []
    
    # Se não houver credenciais cadastradas, gera produtos de teste
    if not APP_ID or not APP_SECRET:
        print("Aviso: Sem credenciais. Gerando catálogo categorizado de teste...")
        return get_mock_categorized_products()

    for nome_cat, query_key in CATEGORIAS.items():
        print(f"Buscando categoria: {nome_cat}...")
        itens = fetch_category_products(query_key, limit=6)
        for item in itens:
            item["categoria"] = nome_cat
            todos_produtos.append(item)
        time.sleep(0.5) # Pausa leve entre requisições

    return todos_produtos if todos_produtos else get_mock_categorized_products()

def get_mock_categorized_products():
    return [
        {"title": "Fone Bluetooth TWS Sem Fio", "price": "R$ 39,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Eletrônicos"},
        {"title": "Smartwatch Esportivo HD", "price": "R$ 89,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Eletrônicos"},
        {"title": "Lâmpada LED RGB Wi-Fi", "price": "R$ 29,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Casa"},
        {"title": "Umidificador de Ar Aromatizador", "price": "R$ 45,00", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Casa"},
        {"title": "Camiseta Algodão Premium Unissex", "price": "R$ 35,00", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Moda"},
        {"title": "Kit Pincéis de Maquiagem Profissional", "price": "R$ 24,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Beleza"}
    ]

def generate_html(produtos):
    # Obtém a lista única de categorias
    categorias_unicas = list(dict.fromkeys([p['categoria'] for p in produtos]))
    
    # Botões das abas
    tabs_html = '<button class="tab-btn active" onclick="filterCategory(\'all\', this)">Todos</button>'
    for cat in categorias_unicas:
        tabs_html += f'<button class="tab-btn" onclick="filterCategory(\'{cat}\', this)">{cat}</button>'

    # Cards dos produtos
    cards_html = ""
    for p in produtos:
        cards_html += f"""
        <div class="card" data-category="{p['categoria']}">
            <div class="img-container">
                <img src="{p['image']}" alt="{p['title']}" loading="lazy">
            </div>
            <div class="card-body">
                <span class="badge">{p['categoria']}</span>
                <h3 class="title">{p['title']}</h3>
                <div class="price">{p['price']}</div>
                <a href="{p['link']}" target="_blank" rel="noopener" class="btn">Ver Oferta</a>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vitrine por Categorias</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: #f4f4f6; padding: 12px; }}
        
        /* Abas de Categorias */
        .tabs {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px; margin-bottom: 12px; scrollbar-width: none; }}
        .tabs::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{ background: #fff; border: 1px solid #ddd; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: #555; white-space: nowrap; cursor: pointer; transition: all 0.2s; }}
        .tab-btn.active {{ background: #ee4d2d; color: #fff; border-color: #ee4d2d; }}
        
        /* Grid e Cards */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #ffffff; border-radius: 8px; border: 1px solid #e5e5e5; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }}
        .img-container {{ width: 100%; height: 150px; background-color: #fafafa; }}
        .card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .card-body {{ padding: 8px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .badge {{ font-size: 0.65rem; background: #fff0ed; color: #ee4d2d; padding: 2px 6px; border-radius: 4px; width: fit-content; margin-bottom: 4px; font-weight: bold; }}
        .title {{ font-size: 0.8rem; color: #222; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.4em; line-height: 1.2; }}
        .price {{ font-size: 1rem; font-weight: 700; color: #ee4d2d; margin-bottom: 8px; }}
        .btn {{ text-align: center; background: #ee4d2d; color: #ffffff; text-decoration: none; padding: 6px 0; border-radius: 4px; font-weight: 600; font-size: 0.8rem; display: block; }}
    </style>
</head>
<body>
    <div class="tabs">
        {tabs_html}
    </div>

    <div class="grid" id="productGrid">
        {cards_html}
    </div>

    <script>
        function filterCategory(category, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            element.classList.add('active');

            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {{
                if (category === 'all' || card.getAttribute('data-category') === category) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Sucesso: Vitrine por categorias gerada em index.html!")

if __name__ == "__main__":
    produtos = get_all_products()
    generate_html(produtos)
