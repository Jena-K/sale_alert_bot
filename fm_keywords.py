import requests
from bs4 import BeautifulSoup
import time
from decouple import config  # Import the config function from decouple

def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def send_telegram_message(bot_token, chat_id, message):
    send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    requests.get(send_url, params=params)

def fetch_posts(url, fetched_posts, keywords, bot_token, chat_id):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        posts = soup.select('div.fm_best_widget ul li')

        for post in posts:
            title_element = post.select_one('div.li h3.title a')
            if not title_element:
                continue

            title = title_element.get_text(strip=True)
            post_url = 'https://www.fmkorea.com' + title_element['href']

            if post_url in fetched_posts:
                continue

            fetched_posts.add(post_url)

            # Check if the title contains any of the keywords
            if any(keyword.lower() in title.lower() for keyword in keywords):
                message = f"{title}\n{post_url}"
                send_telegram_message(bot_token, chat_id, message)

    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    url = 'https://www.fmkorea.com/hotdeal'
    bot_token = config('BOT_TOKEN')  # Load bot_token from .env file
    chat_id = config('CHAT_ID')  # Load chat_id from .env file
    fetched_posts = set()
    keywords = load_keywords('keywords.txt')  # Load keywords from file

    while True:
        fetch_posts(url, fetched_posts, keywords, bot_token, chat_id)
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()