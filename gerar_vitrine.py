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
    if any(w in nome_lower for w in ["fone", "bluetooth", "smartwatch", "relogio", "celular", "gamer", "pc", "led", "cabo", "carregador", "suporte", "camera", "som", "caixa de som", "drone", "tablet", "teclado", "mouse", "usb"]):
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
    elif any(w in nome_lower for w in ["bicicleta", "scooter", "bola", "academia", "elastico", "garrafa", "squeeze", "camping", "pesca", "mochila", "patins", "kimono"]):
        return "Esporte & Lazer"
    
    # Infantil & Brinquedos
    elif any(w in nome_lower for w in ["brinquedo", "boneca", "carrinho", "infantil", "bebe", "fralda", "mordedor", "jogos", "quebra-cabeca"]):
        return "Infantil & Brinquedos"
    
    else:
        return "Outros"

def get_shopee_products():
    if not APP_ID or not APP_SECRET:
        print("Aviso: Chaves não encontradas. Usando catálogo expandido de teste.")
        return get_mock_products()

    timestamp = int(time.time())
    # Limite expandido para 100 produtos
    query = """
    query {
      productOfferV2(page: 1, limit: 100) {
        nodes {
          productName
          price
          imageUrl
          offerLink
        }
      }
    }
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
        
        if not nodes:
            print("Nenhum produto retornado da API. Usando catálogo de teste.")
            return get_mock_products()

        produtos = []
        for item in nodes:
            name = item.get("productName", "Produto Shopee") or "Produto Shopee"
            price_val = safe_float(item.get("price"))
            img = item.get("imageUrl") or "https://via.placeholder.com/250"
            link = item.get("offerLink") or "#"
            cat = categorizar_nome(name)

            produtos.append({
                "title": name,
                "price": f"R$ {price_val:.2f}".replace(".", ","),
                "image": img,
                "link": link,
                "categoria": cat
            })
        return produtos

    except Exception as e:
        print(f"Erro ao conectar com a Shopee: {e}")
        return get_mock_products()

def get_mock_products():
    return [
        {"title": "Fone de Ouvido Bluetooth TWS Sem Fio", "price": "R$ 39,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Eletrônicos & Tech"},
        {"title": "Smartwatch Relógio Esportivo HD", "price": "R$ 89,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Eletrônicos & Tech"},
        {"title": "Jogo de Panelas Antiaderente 5 Peças", "price": "R$ 142,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Casa & Cozinha"},
        {"title": "Cortador de Legumes Multifuncional 16 em 1", "price": "R$ 38,50", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Casa & Cozinha"},
        {"title": "Moletom Canguru Cristão Algodão", "price": "R$ 59,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Moda & Calçados"},
        {"title": "Tênis Running Masculino Respirável", "price": "R$ 79,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Moda & Calçados"},
        {"title": "Kit Eudora Siàge Pro Cronology Tratamento", "price": "R$ 69,99", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Beleza & Saúde"},
        {"title": "Parafusadeira e Furadeira 26V com Maleta", "price": "R$ 119,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Ferramentas & Auto"},
        {"title": "Garrafa Térmica Inox de Água 1 Litro", "price": "R$ 34,90", "image": "https://via.placeholder.com/250", "link": "https://shopee.com.br", "categoria": "Esporte & Lazer"}
    ]

def generate_html(produtos):
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
        body {{ background-color: #f4f4f6; padding: 12px; max-width: 1200px; margin: 0 auto; }}
        
        /* Cabeçalho e Busca */
        .search-box {{ margin-bottom: 12px; position: relative; }}
        .search-input {{
            width: 100%;
            padding: 10px 16px;
            font-size: 0.95rem;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: border-color 0.2s;
        }}
        .search-input:focus {{ border-color: #ee4d2d; }}
        
        /* Abas de Categorias */
        .tabs {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px; margin-bottom: 12px; scrollbar-width: none; }}
        .tabs::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{ background: #fff; border: 1px solid #ddd; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: #555; white-space: nowrap; cursor: pointer; transition: all 0.2s; }}
        .tab-btn.active {{ background: #ee4d2d; color: #fff; border-color: #ee4d2d; }}
        
        /* Grid de Produtos */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }}
        .card {{ background: #ffffff; border-radius: 8px; border: 1px solid #e5e5e5; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }}
        .img-container {{ width: 100%; height: 150px; background-color: #fafafa; }}
        .card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .card-body {{ padding: 8px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .badge {{ font-size: 0.65rem; background: #fff0ed; color: #ee4d2d; padding: 2px 6px; border-radius: 4px; width: fit-content; margin-bottom: 4px; font-weight: bold; }}
        .title {{ font-size: 0.8rem; color: #222; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.4em; line-height: 1.2; }}
        .price {{ font-size: 1rem; font-weight: 700; color: #ee4d2d; margin-bottom: 8px; }}
        .btn {{ text-align: center; background: #ee4d2d; color: #ffffff; text-decoration: none; padding: 6px 0; border-radius: 4px; font-weight: 600; font-size: 0.8rem; display: block; }}
        
        /* Estado Vazio */
        .no-results {{ display: none; text-align: center; padding: 30px 10px; color: #777; font-size: 0.9rem; grid-column: 1 / -1; }}
    </style>
</head>
<body>

    <!-- Campo de Busca -->
    <div class="search-box">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 Pesquisar produtos na vitrine..." oninput="filterProducts()">
    </div>

    <!-- Filtro por Categorias -->
    <div class="tabs">
        {tabs_html}
    </div>

    <!-- Lista de Produtos -->
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
    print("Sucesso: index.html gerado com busca e mais categorias!")

if __name__ == "__main__":
    try:
        prods = get_shopee_products()
        generate_html(prods)
    except Exception as e:
        print(f"Erro durante execução: {e}")
        generate_html(get_mock_products())
