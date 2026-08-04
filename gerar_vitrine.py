import os
import time
import hashlib
import json
import requests

APP_ID = os.getenv("SHOPEE_APP_ID", "").strip()
APP_SECRET = os.getenv("SHOPEE_APP_SECRET", "").strip()

def safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default

def categorizar_nome(nome):
    nome_lower = nome.lower()
    
    # Eletrônicos & Tech
    if any(w in nome_lower for w in ["fone", "bluetooth", "smartwatch", "relogio", "celular", "gamer", "pc", "led", "cabo", "carregador", "suporte", "camera", "som", "caixa", "drone", "tablet", "teclado", "mouse", "usb"]):
        return "Eletrônicos & Tech"
    
    # Casa & Cozinha
    elif any(w in nome_lower for w in ["panela", "jogo", "copo", "cozinha", "casa", "cortador", "jarra", "pote", "mesa", "organizador", "vidro", "toalha", "lixeira", "prato", "talher", "air fryer", "lampada", "tapete", "travesseiro", "lençol"]):
        return "Casa & Cozinha"
    
    # Moda & Calçados
    elif any(w in nome_lower for w in ["vestido", "moletom", "tenis", "shoes", "camisa", "camiseta", "roupa", "bolsa", "oculos", "cristao", "calca", "bermuda", "shorts", "saia", "meia", "chinelo", "sapatilha", "jaqueta", "casaco"]):
        return "Moda & Calçados"
    
    # Beleza & Saúde
    elif any(w in nome_lower for w in ["siage", "eudora", "batom", "maquiagem", "creme", "perfume", "skincare", "cabelo", "shampoo", "condicionador", "esmalte", "pincel", "protetor", "sabonete", "serum"]):
        return "Beleza & Saúde"
    
    # Ferramentas & Auto
    elif any(w in nome_lower for w in ["parafusadeira", "furadeira", "chave", "maleta", "automotivo", "lavadora", "som automotivo", "capacete", "luva", "pneu", "bico", "bomba", "martelo", "alicate"]):
        return "Ferramentas & Auto"
    
    # Esporte & Lazer
    elif any(w in nome_lower for w in ["bicicleta", "scooter", "bola", "academia", "elastico", "garrafa", "squeeze", "camping", "pesca", "mochila", "patins"]):
        return "Esporte & Lazer"
    
    else:
        return "Geral"

def fetch_shopee_products(limit=40):
    if not APP_ID or not APP_SECRET:
        print("Erro: Credenciais SHOPEE_APP_ID e SHOPEE_APP_SECRET não configuradas.")
        return []

    timestamp = int(time.time())
    query = f"""
    query {{
      productOfferV2(page: 1, limit: {limit}) {{
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
        response = requests.post(url, headers=headers, data=payload, timeout=20)
        res_data = response.json()
        nodes = res_data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
        
        produtos = []
        for item in nodes:
            name = item.get("productName") or "Produto Shopee"
            price_val = safe_float(item.get("price"))
            img = item.get("imageUrl") or ""
            link = item.get("offerLink") or "#"
            cat = categorizar_nome(name)

            if img and link != "#":
                produtos.append({
                    "title": name,
                    "price": f"R$ {price_val:.2f}".replace(".", ","),
                    "image": img,
                    "link": link,
                    "categoria": cat
                })
        return produtos

    except Exception as e:
        print(f"Erro ao buscar ofertas na Shopee: {e}")
        return []

def generate_html(produtos):
    if not produtos:
        print("Aviso: Nenhum produto foi retornado da API.")
        produtos = []

    categorias_presentes = list(dict.fromkeys([p["categoria"] for p in produtos]))
    
    tabs_html = '<button class="tab-btn active" onclick="setCategory(\'all\', this)">🔥 Todos</button>'
    for cat in categorias_presentes:
        tabs_html += f'<button class="tab-btn" onclick="setCategory(\'{cat}\', this)">{cat}</button>'

    cards_html = ""
    for p in produtos:
        cards_html += f"""
        <div class="card" data-category="{p['categoria']}" data-title="{p['title'].replace('"', '&quot;')}">
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
    <title>Vitrine Shopee</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: #f4f4f6; padding: 10px; max-width: 1200px; margin: 0 auto; }}
        
        .search-box {{ margin-bottom: 10px; }}
        .search-input {{
            width: 100%;
            padding: 10px 16px;
            font-size: 0.9rem;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            background: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .search-input:focus {{ border-color: #ee4d2d; }}
        
        .tabs {{ display: flex; gap: 6px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 10px; scrollbar-width: none; }}
        .tabs::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{ background: #fff; border: 1px solid #ddd; padding: 6px 14px; border-radius: 18px; font-size: 0.8rem; font-weight: 600; color: #555; white-space: nowrap; cursor: pointer; }}
        .tab-btn.active {{ background: #ee4d2d; color: #fff; border-color: #ee4d2d; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(145px, 1fr)); gap: 10px; }}
        .card {{ background: #ffffff; border-radius: 8px; border: 1px solid #e5e5e5; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }}
        .img-container {{ width: 100%; height: 140px; background-color: #f9f9f9; display: flex; align-items: center; justify-content: center; }}
        .card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .card-body {{ padding: 8px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .badge {{ font-size: 0.65rem; background: #fff0ed; color: #ee4d2d; padding: 2px 6px; border-radius: 4px; width: fit-content; margin-bottom: 4px; font-weight: bold; }}
        .title {{ font-size: 0.78rem; color: #222; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.4em; line-height: 1.2; }}
        .price {{ font-size: 0.95rem; font-weight: 700; color: #ee4d2d; margin-bottom: 8px; }}
        .btn {{ text-align: center; background: #ee4d2d; color: #ffffff; text-decoration: none; padding: 6px 0; border-radius: 4px; font-weight: 600; font-size: 0.8rem; display: block; }}
        
        .no-results {{ display: none; text-align: center; padding: 30px; color: #777; grid-column: 1 / -1; }}
    </style>
</head>
<body>

    <div class="search-box">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 Pesquisar produtos na vitrine..." oninput="filterProducts()">
    </div>

    <div class="tabs">
        {tabs_html}
    </div>

    <div class="grid" id="productGrid">
        {cards_html}
        <div class="no-results" id="noResults">
            Nenhum produto encontrado para sua busca. 🙁
        </div>
    </div>

    <script>
        let currentCategory = 'all';

        function setCategory(category, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            element.classList.add('active');
            currentCategory = category;
            filterProducts();
        }}

        function filterProducts() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.card');
            let visibleCount = 0;

            cards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const title = card.getAttribute('data-title').toLowerCase();

                const matchesCategory = (currentCategory === 'all' || cat === currentCategory);
                const matchesSearch = query === '' || title.includes(query) || cat.toLowerCase().includes(query);

                if (matchesCategory && matchesSearch) {{
                    card.style.display = 'flex';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            const noResults = document.getElementById('noResults');
            if (noResults) {{
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }}
        }}
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Sucesso: index.html gerado com sucesso!")

if __name__ == "__main__":
    prods = fetch_shopee_products(limit=40)
    generate_html(prods)
