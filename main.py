import requests
import time
from datetime import datetime
from flask import Flask
from threading import Thread

# === CONFIG ===
BOT_TOKEN = '7585752271:AAFzQM-SfgmXmynKpHe_fT_iLg7wLrALwu8'
CHANNEL_USERNAME = '@ALLnews_24hours'
GNEWS_API_KEY = '1a9f20f23ac2d7016180cec977baa718'
NEWS_API_URL = f'https://gnews.io/api/v4/top-headlines?lang=hi&country=in&token={GNEWS_API_KEY}'

# === Flask Web Server to Keep Alive ===
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and posting news every 30 minutes!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === News Bot Functions ===
posted_titles = set()

def get_today_news():
    try:
        response = requests.get(NEWS_API_URL)
        articles = response.json().get("articles", [])
        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def send_news_to_channel(article):
    try:
        title = article.get("title", "No title")
        url = article.get("url", "")
        content = article.get("description", "")
        image = article.get("image", "")

        caption = f"*{title}*\n\n{content}\n\n[पूरा पढ़ें]({url})"
        payload = {
            "chat_id": CHANNEL_USERNAME,
            "photo": image if image else "https://via.placeholder.com/300",
            "caption": caption,
            "parse_mode": "Markdown"
        }
        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data=payload)
        print(f"[{datetime.now()}] Sent: {title}")
    except Exception as e:
        print(f"Error sending news: {e}")

def main_loop():
    # Post immediately when bot starts
    print(f"[{datetime.now()}] Sending first post...")
    articles = get_today_news()
    for article in articles:
        title = article.get("title", "")
        if title and title not in posted_titles:
            send_news_to_channel(article)
            posted_titles.add(title)
            break

    while True:
        print(f"[{datetime.now()}] Waiting 30 minutes...")
        time.sleep(1800)  # 30 minutes

        print(f"[{datetime.now()}] Checking for new news...")
        articles = get_today_news()
        for article in articles:
            title = article.get("title", "")
            if title and title not in posted_titles:
                send_news_to_channel(article)
                posted_titles.add(title)
                break  # Send only 1 new post every 30 minutes

# === Start Everything ===
keep_alive()
main_loop()
