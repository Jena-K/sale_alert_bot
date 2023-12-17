import tkinter as tk
from threading import Thread, Event, Timer
import requests, os, sys
from bs4 import BeautifulSoup
from decouple import config
from dotenv import load_dotenv

# 키워드 목록 불러오기
def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]
    
# 텔레그램 메시지 전송
def send_telegram_message(bot_token, chat_id, message):
    
    send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    requests.get(send_url, params=params)
    
# 키워드에 맞는 게시글 가져오기
def fetch_posts(url, fetched_posts, bot_token, chat_id, keywords):
    try:
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
            
            # Check if the title contains any of the keywords
            if any(keyword.lower() in title.lower() for keyword in keywords):
                message = f"{title}\n{post_url}"
                message_thread = Thread(target=send_telegram_message, args=[bot_token, chat_id, message])
                message_thread.start()
                
    except Exception as e:
        print(f"Error occurred: {e}")
        
# GUI functions
def start_scraping():
    global stop_event, fetched_posts
    stop_event.clear()
    fetched_posts = set()
    
    schedule_fetch(stop_event, interval, 'https://www.fmkorea.com/hotdeal', fetched_posts, bot_token, chat_id, keywords)
    start_button.config(text="Restart", command=restart_scraping)
    
def restart_scraping():
    global keywords
    stop_event.set()
    keywords = load_keywords('keywords.txt')
    start_scraping()
    
def stop_scraping():
    stop_event.set()
    window.destroy()
    
def on_close():
    stop_event.set()
    window.destroy()
    
def schedule_fetch(stop_event, interval, url, fetched_posts, bot_token, chat_id, keywords):
    if not stop_event.is_set():
        fetch_posts(url, fetched_posts, bot_token, chat_id, keywords)
        Timer(interval, schedule_fetch, [stop_event, interval, url, fetched_posts, bot_token, chat_id, keywords]).start()
        
#set global value
url = 'https://www.fmkorea.com/hotdeal'

# Determine if the application is frozen (compiled with PyInstaller)
if getattr(sys, 'frozen', False):
    # The application is frozen
    application_path = sys._MEIPASS
else:
    # The application is not frozen
    application_path = os.path.dirname(os.path.abspath(__file__))

# Path to .env file
env_path = os.path.join(application_path, '.env')

# Load .env file
load_dotenv(env_path)

# Access BOT_TOKEN and CHAT_ID
bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')
interval = 10

# dotenv 대신 config 사용했을 경우 ----------------- 
# if getattr(sys, 'frozen', False):
#     # The application is frozen
#     env_path = os.path.join(sys._MEIPASS, '.env')
# else:
#     # The application is not frozen
#     env_path = '.env'

# config.read_env(env_path)

# bot_token = config('BOT_TOKEN')
# chat_id = config('CHAT_ID')
# interval = 10
#----------------------------------------------------

# Initialize threading event
stop_event = Event()

# Load keywords initially
keywords = load_keywords('keywords.txt')

# GUI setup
window = tk.Tk()
window.title("Bot")
window.geometry("200x80")
window.protocol("WM_DELETE_WINDOW", on_close)

# Calculate the center position
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
center_x = int(screen_width/2 - 300/2)
center_y = int(screen_height/2 - 150/2)

# Position the window in the center of the screen
window.geometry(f"+{center_x}+{center_y}")

# Frame for buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=20)

# Start and Exit buttons inside the frame
start_button = tk.Button(button_frame, text="Start", command=start_scraping)
start_button.pack(side=tk.LEFT, padx=10)

exit_button = tk.Button(button_frame, text="Exit", command=stop_scraping)
exit_button.pack(side=tk.LEFT, padx=10)

# Start the GUI event loop
window.mainloop()
