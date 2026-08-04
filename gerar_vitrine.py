import os
import time
import hashlib
import json
import requests

# Busca as chaves das variáveis de ambiente do GitHub Actions
APP_ID = os.getenv("SHOPEE_APP_ID", "").strip()
APP_SECRET = os.getenv("SHOPEE_APP_SECRET", "").strip()

def fetch_shopee_products():
    """
    Busca os produtos na API de Afiliados da Shopee.
    Se não houver credenciais ou ocorrer erro, retorna produtos de exemplo.
    """
    if not APP_ID or not APP_SECRET:
        print("Aviso: SHOPEE_APP_ID ou SHOPEE_APP_SECRET não foram configurados. Usando produtos de teste.")
        return get_mock_products()

    timestamp = int(time.time())
    query = """
    query {
      productOfferV2(page: 1, limit: 12) {
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
            
        if produtos:
            print(f"Sucesso! {len(produtos)} produtos obtidos da API da Shopee.")
            return produtos
        else:
            print("Nenhum produto retornado da API. Usando produtos de exemplo.")
            return get_mock_products()

    except Exception as e:
        print(f"Erro ao conectar com a API da Shopee: {e}")
        return get_mock_products()

def get_mock_products():
    return [
        {
            "title": "Fone de Ouvido Bluetooth Sem Fio TWS Premium",
            "price": "R$ 39,90",
            "image": "https://via.placeholder.com/250x250?text=Fone+Bluetooth",
            "link": "https://shopee.com.br"
        },
        {
            "title": "Smartwatch Relógio Inteligente Esportivo HD",
            "price": "R$ 89,90",
            "image": "https://via.placeholder.com/250x250?text=Smartwatch",
            "link": "https://shopee.com.br"
        },
        {
            "title": "Mochila Impermeável com Entrada USB",
            "price": "R$ 65,00",
            "image": "https://via.placeholder.com/250x250?text=Mochila",
            "link": "https://shopee.com.br"
        },
        {
            "title": "Lâmpada LED RGB Inteligente Wi-Fi",
            "price": "R$ 29,90",
            "image": "https://via.placeholder.com/250x250?text=Lampada+LED",
            "link": "https://shopee.com.br"
        }
    ]

def generate_html(produtos):
    cards_html = ""
    for p in produtos:
        cards_html += f"""
        <div class="card">
            <div class="img-container">
                <img src="{p['image']}" alt="{p['title']}" loading="lazy">
            </div>
            <div class="card-body">
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
    <title>Vitrine de Ofertas Shopee</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #f4f4f6; padding: 12px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #ffffff; border-radius: 8px; border: 1px solid #e5e5e5; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s, box-shadow 0.2s; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .img-container {{ width: 100%; height: 160px; background-color: #fafafa; overflow: hidden; }}
        .card img {{ width: 100%; height: 100%; object-fit: cover; }}
        .card-body {{ padding: 10px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }}
        .title {{ font-size: 0.85rem; color: #222; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.4em; line-height: 1.2; font-weight: 500; }}
        .price {{ font-size: 1.1rem; font-weight: 700; color: #ee4d2d; margin-bottom: 10px; }}
        .btn {{ text-align: center; background: #ee4d2d; color: #ffffff; text-decoration: none; padding: 8px 0; border-radius: 4px; font-weight: 600; font-size: 0.85rem; display: block; transition: background 0.2s; }}
        .btn:hover {{ background: #d73211; }}
    </style>
</head>
<body>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Sucesso: Arquivo 'index.html' gerado com êxito!")

if __name__ == "__main__":
    produtos = fetch_shopee_products()
    generate_html(produtos)
