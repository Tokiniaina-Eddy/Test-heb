from flask import Flask, jsonify
import os
from dotenv import load_dotenv

import praw
import re
import pandas as pd
from datetime import datetime
from flask_cors import CORS

reddit = praw.Reddit(
    client_id="HDUed5b4vjaJstyiy5r0Ow",
    client_secret="pEI862BffKu6gwbWSQcPBz9Kn_dnEQ",
    user_agent="SubredditScraper/1.0"
)
def extract_price(text):
    price_pattern = r'(\$|€|£)\s?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
    match = re.search(price_pattern, text)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return "N/A"

def scrape_hot_and_sort(keywords, subreddits="all", limit=50):
    print(f"--- Recherche HOT: '{keywords}' dans r/{subreddits} ---")
    
    products_data = []
    subreddit = reddit.subreddit(subreddits)
    
    # ICI : On demande à l'API de trier par 'hot' directement
    # Cela nous donne les posts "tendance" (récents + actifs)
    search_results = subreddit.search(keywords, sort='hot', limit=limit)
    
    for submission in search_results:
        # On capture tout
        full_text = f"{submission.title} {submission.selftext}"
        
        product_info = {
            'titre': submission.title,
            'prix_estime': extract_price(full_text),
            'score': submission.score,        # Le point crucial
            'nb_commentaires': submission.num_comments,
            'url': submission.url,
            'date': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'),
            'subreddit': submission.subreddit.display_name
        }
        
        products_data.append(product_info)
    
    df = pd.DataFrame(products_data)
    
    # ICI : Votre demande spécifique
    # On prend les résultats "Hot" et on les réorganise pour afficher les plus gros scores en haut
    if not df.empty:
        df = df.sort_values(by='score', ascending=False)
        
    return df


app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    query = "selling computer"
    subs = "hardwareswap"

    df_hot = scrape_hot_and_sort(query, subs, limit=50)

    if not df_hot.empty:
        
        test = df_hot.to_json(orient='records')
        return jsonify(test)
    else:
        return jsonify({"message": "No results found"})


@app.route('/test')
def test():
    data = {
        'message': 'Hello, World!',
        'name': 'Test API'
    }
    return data

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)