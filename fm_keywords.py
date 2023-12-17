import requests
from bs4 import BeautifulSoup
import time, sqlite3
from pprint import pprint
from decouple import config  # Import the config function from decouple

def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

# alert_messages: [chat_ids, title, post_url]
def send_telegram_message(alert_messages, bot_token):
    
    for alert_message in alert_messages:
        chat_ids, title, post_url = alert_message
        message = f"{title}\n{post_url}"
        
        for chat_id in chat_ids:
            send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            params = {'chat_id': chat_id, 'text': message}
            requests.get(send_url, params=params)

def fetch_chat_ids(posts_to_fetch):
    alert_messages = []

    # Connect to database
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()
    
    for title, post_url in posts_to_fetch:
        chat_ids = set()
        
        # Fetch keywords for the user associated with this post
        cursor.execute('SELECT user_id, keyword FROM keywords')
        user_keywords = [row for row in cursor.fetchall()]
        
        for chat_id, keyword in user_keywords:
            if keyword.lower() in title.lower():
                chat_ids.add(chat_id)
        
        alert_messages.append([chat_ids, title, post_url])
        
    conn.close()
    
    return alert_messages

def fetch_posts(url, fetched_posts):
    try:
        posts_to_fetch = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        posts = soup.select('div.fm_best_widget ul li')

        for post in posts:
            title_element = post.select_one('div.li h3.title a')

            title = title_element.get_text(strip=True)
            post_url = 'https://www.fmkorea.com' + title_element['href']

            if post_url in fetched_posts:
                continue

            fetched_posts.add(post_url)
            
            posts_to_fetch.append((title, post_url))

        return posts_to_fetch
    
    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    url = 'https://www.fmkorea.com/hotdeal'
    bot_token = config('BOT_TOKEN')  # Load bot_token from .env file
    fetched_posts = set()

    while True:
        posts_to_fetch = fetch_posts(url, fetched_posts)
        alert_messages = fetch_chat_ids(posts_to_fetch)
        send_telegram_message(alert_messages, bot_token)
        
        time.sleep(10)  # Check every 10 seconds
    
if __name__ == "__main__":
    main()
