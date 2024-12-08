import requests
import os
from dotenv import load_dotenv
load_dotenv()

COINGECKO_API_KEY = os.environ.get('COINGECKO_API_KEY')
headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": COINGECKO_API_KEY
        }

def fetch_coin_list():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url,headers)
    if response.status_code == 200:
        data = response.json()
        return build_symbol_to_id_map(data)
    else:
        print("Errore nel download della lista:", response.status_code)

def build_symbol_to_id_map(coin_list):
    return {coin["symbol"].upper(): coin["id"] for coin in coin_list}


def coingecko_sentiment(symbol, list):
    try:
        url = "https://api.coingecko.com/api/v3/coins/"+list[symbol]
        # Effettua una richiesta GET all'API
        response = requests.get(url, headers)
        # Controlla lo stato della risposta
        if response.status_code == 200:
            data = response.json()
            
            # Estrai metriche sociali
            social_data = f"*Position: {symbol} Twitter Followers: {data.get('community_data').get('twitter_followers')} Sentiments Votes UP: {data.get('sentiment_votes_up_percentage')} Sentiments Votes Down: {data.get('sentiment_votes_down_percentage')}\n"
            return social_data
        else:
            print(f"Errore: Stato HTTP {response.status_code}")
    except Exception as e:
        print("Errore durante la richiesta API:", e)
