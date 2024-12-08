import requests
import os
from dotenv import load_dotenv
load_dotenv()

NEWS_API_KEY = os.environ.get('NEWS_API_KEY')

# URL dell'API per ottenere le criptovalute di tendenza
url = "https://newsapi.org/v2/top-headlines?q=crypto&apiKey="+NEWS_API_KEY

def news_topheadlines():
    try:
        # Effettua una richiesta GET all'API
        response = requests.get(url)
        
        # Controlla lo stato della risposta
        if response.status_code == 200:
            data = response.json()
            
            # Estrai le criptovalute di tendenza
            articles = data.get("articles", [])
            articles_list = ''
            
            for article in articles:
                articles_list += f"*Title: {article.get('title')} Description: ({article.get('description')})\n"
            
            return articles_list
        else:
            print(f"Errore: Stato HTTP {response.status_code}")
    except Exception as e:
        print("Errore durante la richiesta API:", e)
