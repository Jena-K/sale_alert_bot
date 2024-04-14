"""
Dependencies:
    - Python 3.11.9
    
Usage:
    $ python ./app.py

"""
import tkinter as tk
from threading import Thread, Event, Timer
import requests, os, sys
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tkinter import font as tkFont

# Target URL
url = 'https://www.fmkorea.com/hotdeal'

# Determine if the application is frozen (compiled with PyInstaller)
def initialize_environment():
    if getattr(sys, 'frozen', False):
        # When application is frozen
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(application_path, '.env')
    load_dotenv(env_path)
    
    return os.getenv('BOT_TOKEN'), os.getenv('CHAT_ID')

def fetch_and_notify(url, fetched_posts, bot_token, chat_id, keywords):
    posts_to_send = []
    try:
        response = requests.get(url)
        for post in BeautifulSoup(response.content, 'html.parser').select('div.fm_best_widget ul li'):
            title, post_url = post_data(post)
            if post_url not in fetched_posts and is_keyword_present(title, keywords):
                posts_to_send.append([title, post_url])
        fetched_posts.union(list(zip(*posts_to_send))[1])
        notify_telegram(bot_token, chat_id, posts_to_send)
    except Exception as e:
        print(f"Error occurred: {e}")

def post_data(post):
    title_element = post.select_one('div.li h3.title a')
    return title_element.get_text(strip=True), 'https://www.fmkorea.com' + title_element['href']

def is_keyword_present(title, keywords):
    return any(keyword.lower() in title.lower() for keyword in keywords) or 'NEW' in keywords

def notify_telegram(bot_token, chat_id, posts): 
    '''send_telegram_messages'''
    for title, post_url in posts:
        message = f"{title}\n{post_url}"
        Thread(target=send_telegram_message, args=(bot_token, chat_id, message)).start()

def send_telegram_message(bot_token, chat_id, message):
    requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage', params={'chat_id': chat_id, 'text': message})

def load_keywords(file_path):
    """Load and return a list of keywords from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

def schedule_fetch(event, interval, url, fetched_posts, bot_token, chat_id, keywords):
    if not event.is_set():
        fetch_and_notify(url, fetched_posts, bot_token, chat_id, keywords)
        Timer(interval, schedule_fetch, args=(event, interval, url, fetched_posts, bot_token, chat_id, keywords)).start()

# Fetch posts containing keywords
def fetch_posts(url, fetched_posts, bot_token, chat_id, keywords):
    """Fetch and process posts from a URL, sending notifications for new posts matching keywords."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        posts = soup.select('div.fm_best_widget ul li')

        for post in posts:
            title_element = post.select_one('div.li h3.title a')
            title = title_element.get_text(strip=True)
            post_url = 'https://www.fmkorea.com' + title_element['href']

            if post_url not in fetched_posts:
                fetched_posts.add(post_url)
                
                # Check if the title contains any of the keywords
                if any(keyword.lower() in title.lower() for keyword in keywords) or ('NEW' in keywords):
                    message = f"{title}\n{post_url}"    
                    message_thread = Thread(target=send_telegram_message, args=(bot_token, chat_id, message))
                    message_thread.start()
                
    except Exception as e:
        print(f"Error occurred: {e}")

def start_scraping(event, button, bot_token, chat_id, keywords):
    if not event.is_set():
        button.config(text="Stop")
        event.set()
        schedule_fetch(event, 120, url, set(), bot_token, chat_id, keywords)
    else :
        button.config(text="Start")
        event.clear()
    
def schedule_fetch(event, interval, url, fetched_posts, bot_token, chat_id, keywords):
    if not event.is_set():
        fetch_and_notify(url, fetched_posts, bot_token, chat_id, keywords)
        Timer(interval, schedule_fetch, args=(event, interval, url, fetched_posts, bot_token, chat_id, keywords)).start()
        
#set global value
url = 'https://www.fmkorea.com/hotdeal'

def setup_gui(stop_event, bot_token, chat_id, keywords):
    window = tk.Tk()
    window.title("FM BOT")
    window.geometry(
        f"+{int(window.winfo_screenwidth() / 2)}+{int(window.winfo_screenheight() / 2)}"
    )
    window.protocol("WM_DELETE_WINDOW", lambda: window.destroy)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)

    custom_font = tkFont.Font(family='Helvetica', size=10)
    button = tk.Button(button_frame, text="Start", width=7, height=2, command=lambda: start_scraping(stop_event, button, bot_token, chat_id, keywords), font=custom_font)
    button.pack(side=tk.LEFT, padx=10)
    # exit_button = tk.Button(button_frame, text="Exit", width=7, height=2, command=lambda: stop_scraping(stop_event, window), font=custom_font)
    # exit_button.pack(side=tk.LEFT, padx=10)

    window.mainloop()

if __name__ == "__main__":
    bot_token, chat_id = initialize_environment()
    keywords = load_keywords(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keywords.txt'))
    setup_gui(Event(), bot_token, chat_id, keywords)