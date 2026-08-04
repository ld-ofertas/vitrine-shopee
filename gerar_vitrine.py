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
    
    if any(w in nome_lower for w in [
        "fone", "bluetooth", "smartwatch", "relogio", "celular", "gamer", "pc", "led", 
        "cabo", "carregador", "suporte", "camera", "som", "caixa", "drone", "tablet", 
        "teclado", "mouse", "usb", "alexa", "caixinha", "repetidor", "memoria", "ssd", 
        "pendrive", "adaptador", "microfone", "headset"
    ]):
        return "Eletrônicos & Tech"
    elif any(w in nome_lower for w in [
        "panela", "jogo", "copo", "cozinha", "casa", "cortador", "jarra", "pote", "mesa", 
        "organizador", "vidro", "toalha", "lixeira", "prato", "talher", "air fryer", 
        "lampada", "tapete", "travesseiro", "lençol", "almofada", "frigideira", "espelho", 
        "prateleira", "cortina", "edredom", "cobertor", "mop", "vassoura"
    ]):
        return "Casa & Cozinha"
    elif any(w in nome_lower for w in [
        "vestido", "moletom", "tenis", "shoes", "camisa", "camiseta", "roupa", "bolsa", 
        "oculos", "cristao", "calca", "bermuda", "shorts", "saia", "meia", "chinelo", 
        "sapatilha", "jaqueta", "casaco", "mochila", "carteira", "cinto", "boné"
    ]):
        return "Moda & Calçados"
    elif any(w in nome_lower for w in [
        "siage", "eudora", "batom", "maquiagem", "creme", "perfume", "skincare", "cabelo", 
        "shampoo", "condicionador", "esmalte", "pincel", "protetor", "sabonete", "serum", 
        "locao", "desodorante", "base", "rimel", "secador", "chapinha", "babyliss"
    ]):
        return "Beleza & Saúde"
    elif any(w in nome_lower for w in [
        "brinquedo", "bebe", "infantil", "fralda", "mamadeira", "carrinho", "pelucia", 
        "boneca", "quebra cabeca", "mordedor", "babador", "chupeta"
    ]):
        return "Infantil & Brinquedos"
    elif any(w in nome_lower for w in [
        "cachorro", "gato", "pet", "racao", "coleira", "arranhador", "comedouro", "tapete higienico"
    ]):
        return "Pet Shop"
    elif any(w in nome_lower for w in [
        "parafusadeira", "furadeira", "chave", "maleta", "automotivo", "lavadora", 
        "som automotivo", "capacete", "luva", "pneu", "bico", "bomba", "martelo", "alicate"
    ]):
        return "Ferramentas & Auto"
    elif any(w in nome_lower for w in [
        "bicicleta", "scooter", "bola", "academia", "elastico", "garrafa", "squeeze", 
        "camping", "pesca", "patins", "suplemento", "whey", "halter"
    ]):
        return "Esporte & Lazer"
    else:
        return "Outras Ofertas"

TERMOS_BUSCA = [
    "fone bluetooth", "smartwatch", "carregador celular", "caixa de som bluetooth", "teclado gamer", "mouse sem fio",
    "air fryer", "jogo de panelas", "mop limpeza", "organizador de cozinha", "lampada led", "jogo de cama",
    "tenis masculino", "vestido feminino", "moletom", "bolsa feminina", "oculos de sol", "relogio masculino",
    "perfume eudora", "kit maquiagem", "skincare", "shampoo siage", "secador de cabelo", "protetor solar",
    "brinquedo educativo", "carrinho controle remoto", "fralda bebe", "boneca",
    "racao cachorro", "arranhador gato", "tapete higienico",
    "parafusadeira", "kit ferramentas", "capacete moto",
    "garrafa termica", "bicicleta", "elastico exercicio"
]

def fetch_shopee_products():
    if not APP_ID or not APP_SECRET:
        print("Erro: Credenciais SHOPEE_APP_ID e SHOPEE_APP_SECRET não configuradas.")
        return []

    url = "https://open-api.affiliate.shopee.com.br/graphql"
    todos_produtos = []
    links_vistos = set()

    for kw in TERMOS_BUSCA:
        timestamp = int(time.time())
        query = f"""
        query {{
          productOfferV2(keyword: "{kw}", page: 1, limit: 30) {{
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

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            res_data = response.json()
            nodes = res_data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
            for item in nodes:
                name = item.get("productName") or "Produto Shopee"
                price_val = safe_float(item.get("price"))
                img = item.get("imageUrl") or ""
                link = item.get("offerLink") or "#"
                cat = categorizar_nome(name)

                if img and link != "#" and link not in links_vistos:
                    links_vistos.add(link)
                    todos_produtos.append({
                        "title": name,
                        "price": f"R$ {price_val:.2f}".replace(".", ","),
                        "image": img,
                        "link": link,
                        "categoria": cat
                    })
            time.sleep(0.1)
        except Exception as e:
            print(f"Erro ao buscar termo '{kw}': {e}")

    for page in range(1, 11):
        timestamp = int(time.time())
        query = f"""
        query {{
          productOfferV2(page: {page}, limit: 50) {{
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

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            res_data = response.json()
            nodes = res_data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
            for item in nodes:
                name = item.get("productName") or "Produto Shopee"
                price_val = safe_float(item.get("price"))
                img = item.get("imageUrl") or ""
                link = item.get("offerLink") or "#"
                cat = categorizar_nome(name)

                if img and link != "#" and link not in links_vistos:
                    links_vistos.add(link)
                    todos_produtos.append({
                        "title": name,
                        "price": f"R$ {price_val:.2f}".replace(".", ","),
                        "image": img,
                        "link": link,
                        "categoria": cat
                    })
            time.sleep(0.1)
        except Exception as e:
            print(f"Erro ao buscar ofertas gerais pag {page}: {e}")

    return todos_produtos

def generate_html(produtos):
    categorias_ordenadas = [
        "Eletrônicos & Tech", "Casa & Cozinha", "Moda & Calçados", 
        "Beleza & Saúde", "Infantil & Brinquedos", "Pet Shop", 
        "Ferramentas & Auto", "Esporte & Lazer", "Outras Ofertas"
    ]
    categorias_presentes = [c for c in categorias_ordenadas if any(p["categoria"] == c for p in produtos)]
    
    tabs_html = '<button class="tab-btn active" onclick="setCategory(\'all\', this)">🔥 Todos</button>'
    for cat in categorias_presentes:
        tabs_html += f'<button class="tab-btn" onclick="setCategory(\'{cat}\', this)">{cat}</button>'

    cards_html = ""
    for p in produtos:
        title_escaped = p['title'].replace('"', '&quot;')
        cards_html += f"""
        <div class="card" data-category="{p['categoria']}" data-title="{title_escaped}">
            <div class="img-container">
                <img src="{p['image']}" alt="{title_escaped}" loading="lazy">
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
    <meta name="theme-color" content="#ee4d2d">
    <link rel="manifest" href="manifest.json">
    <title>Vitrine Shopee</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background-color: #f4f4f6; padding: 10px; max-width: 1200px; margin: 0 auto; }}
        
        .app-banner {{
            background: linear-gradient(135deg, #ee4d2d, #ff7337);
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(238, 77, 45, 0.25);
        }}
        .app-banner-info {{ display: flex; align-items: center; gap: 10px; }}
        .app-banner-icon {{ font-size: 1.5rem; }}
        .app-banner-text h4 {{ font-size: 0.85rem; font-weight: 700; margin-bottom: 2px; }}
        .app-banner-text p {{ font-size: 0.72rem; opacity: 0.95; }}
        .app-banner-actions {{ display: flex; align-items: center; gap: 8px; }}
        .app-install-btn {{
            background: #ffffff;
            color: #ee4d2d;
            border: none;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .app-close-btn {{
            background: none;
            border: none;
            color: #ffffff;
            font-size: 1.1rem;
            cursor: pointer;
            padding: 0 4px;
            opacity: 0.8;
        }}

        .search-box {{ margin-bottom: 8px; }}
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
        
        .counter-bar {{
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 8px;
            padding-left: 4px;
            font-weight: 500;
        }}

        .tabs {{ display: flex; gap: 6px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 10px; scrollbar-width: none; }}
        .tabs::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{ background: #fff; border: 1px solid #ddd; padding: 6px 14px; border-radius: 18px; font-size: 0.8rem; font-weight: 600; color: #555; white-space: nowrap; cursor: pointer; transition: all 0.2s; }}
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
        
        .load-more-container {{ text-align: center; margin: 20px 0 10px 0; }}
        .load-more-btn {{
            background: #fff;
            color: #ee4d2d;
            border: 2px solid #ee4d2d;
            padding: 10px 24px;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .load-more-btn:hover {{ background: #ee4d2d; color: #fff; }}

        .no-results {{ display: none; text-align: center; padding: 30px; color: #777; grid-column: 1 / -1; }}
    </style>
</head>
<body>

    <div class="app-banner" id="appBanner">
        <div class="app-banner-info">
            <span class="app-banner-icon">📲</span>
            <div class="app-banner-text">
                <h4>Instale nosso App de Ofertas</h4>
                <p>Acesse as promoções direto da tela do seu celular</p>
            </div>
        </div>
        <div class="app-banner-actions">
            <button class="app-install-btn" onclick="handleInstallApp()">Instalar</button>
            <button class="app-close-btn" onclick="closeAppBanner()">✕</button>
        </div>
    </div>

    <div class="search-box">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 Pesquisar em centenas de produtos..." oninput="onSearchChange()">
    </div>

    <div class="counter-bar" id="counterBar">
        Carregando produtos...
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

    <div class="load-more-container">
        <button class="load-more-btn" id="loadMoreBtn" onclick="loadMore()">➕ Carregar Mais Produtos</button>
    </div>

    <script>
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js');
        }}

        let deferredPrompt = null;

        // Captura o evento nativo de instalação do Android
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            const banner = document.getElementById('appBanner');
            if (banner) banner.style.display = 'flex';
        }});

        function handleInstallApp() {{
            // Se estiver dentro do Google Sites (iframe)
            if (window.self !== window.top) {{
                window.open('https://aleandrogefune05-bot.github.io', '_blank');
                return;
            }}

            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        closeAppBanner();
                    }}
                    deferredPrompt = null;
                }});
            }} else {{
                alert("O navegador ainda está preparando o instalador.\\n\\nAguarde alguns segundos e tente novamente, ou use o menu de 3 pontinhos do Chrome > 'Instalar aplicativo'.");
            }}
        }}

        function closeAppBanner() {{
            const banner = document.getElementById('appBanner');
            if (banner) banner.style.display = 'none';
        }}

        let currentCategory = 'all';
        let visibleLimit = 24;
        const PAGE_SIZE = 24;

        function setCategory(category, element) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            element.classList.add('active');
            currentCategory = category;
            visibleLimit = PAGE_SIZE;
            filterProducts();
        }}

        function onSearchChange() {{
            visibleLimit = PAGE_SIZE;
            filterProducts();
        }}

        function filterProducts() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = Array.from(document.querySelectorAll('.card'));
            
            let matchingCards = [];

            cards.forEach(card => {{
                const cat = card.getAttribute('data-category');
                const title = card.getAttribute('data-title').toLowerCase();

                const matchesCategory = (currentCategory === 'all' || cat === currentCategory);
                const matchesSearch = query === '' || title.includes(query) || cat.toLowerCase().includes(query);

                if (matchesCategory && matchesSearch) {{
                    matchingCards.push(card);
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            matchingCards.forEach((card, index) => {{
                if (index < visibleLimit) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            const counterBar = document.getElementById('counterBar');
            const showing = Math.min(visibleLimit, matchingCards.length);
            if (counterBar) {{
                counterBar.innerText = `Exibindo ${{showing}} de ${{matchingCards.length}} ofertas disponíveis`;
            }}

            const loadMoreBtn = document.getElementById('loadMoreBtn');
            if (loadMoreBtn) {{
                if (visibleLimit < matchingCards.length) {{
                    loadMoreBtn.style.display = 'inline-block';
                }} else {{
                    loadMoreBtn.style.display = 'none';
                }}
            }}

            const noResults = document.getElementById('noResults');
            if (noResults) {{
                noResults.style.display = matchingCards.length === 0 ? 'block' : 'none';
            }}
        }}

        function loadMore() {{
            visibleLimit += PAGE_SIZE;
            filterProducts();
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            filterProducts();
        }});
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Sucesso: index.html gerado!")

if __name__ == "__main__":
    prods = fetch_shopee_products()
    generate_html(prods)
