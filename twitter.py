import tweepy
import os
from dotenv import load_dotenv
load_dotenv()

# Bearer Token (API v2)
BEARER_TOKEN = os.environ.get('BEARER_TOKEN')

# Creazione del client Tweepy per API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def search_tweets_by_hashtag(hashtag, max_results=10):
    query = f"#{hashtag}"  # Query per l'hashtag
    response = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=["author_id", "created_at", "text"])
    recent_headlines = ''
    if response.data:
        for tweet in response.data:
            recent_headlines += ("*User: {tweet.author_id}\n"
                     "*Tweet: {tweet.text}\n")
        return recent_headlines

print(search_tweets_by_hashtag("SUI", max_results=10))