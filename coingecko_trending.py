import requests
import os
from dotenv import load_dotenv
load_dotenv()

COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY')

# URL dell'API per ottenere le criptovalute di tendenza
url = "https://api.coingecko.com/api/v3/search/trending"
headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": COINGECKO_API_KEY
        }

def coingecko_trending():
    try:
        # Effettua una richiesta GET all'API
        response = requests.get(url,headers)
        
        # Controlla lo stato della risposta
        if response.status_code == 200:
            data = response.json()
            
            # Estrai le criptovalute di tendenza
            trending_coins = data.get("coins", [])
            trending_list = ''
            
            for coin in trending_coins:
                coin_info = coin.get("item", {})
                trending_list += f"*Coin: {coin_info.get('name')} Symbol: ({coin_info.get('symbol')}) Market Cap Rank: {coin_info.get('market_cap_rank')}  Actual price in BTC: {coin_info.get('price_btc')} Score: {coin_info.get('score')}\n"
            
            return trending_list
        else:
            print(f"Errore: Stato HTTP {response.status_code}")
    except Exception as e:
        print("Errore durante la richiesta API:", e)
