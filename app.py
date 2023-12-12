import requests
from bs4 import BeautifulSoup
import time, subprocess, sqlite3

from flask import Flask, request
from decouple import config  # Import the config function from decouple

# Load the bot token and chat ID from the .env file
BOT_TOKEN = config('BOT_TOKEN')
CHAT_ID = config('CHAT_ID')

# List to store keywords
keywords = []

# Initialize Flask app
app = Flask(__name__)

# Run get items
subprocess.Popen(['python', 'fm_keywords.py'])
subprocess.run(['python', 'create_db.py'])

# Define a route to handle incoming updates from Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json

    # Check if the update contains a message
    if 'message' in update:
        message = update['message']
        user_id = message['from'].get('id', '')
        text = message.get('text', 'Error Empty key')
        keyword = text[text.find(' ')+1:].strip()
        

        # Handle /add_key command
        if text.startswith('/addkey '):
            print(user_id, keyword)
            add_keyword(user_id, keyword)

        # Handle /del_key command
        elif text.startswith('/delkey '):
            delete_keyword(user_id, keyword)

    return 'success', 200

# # Function to add a keyword to the list
# def add_key(text):
#     keyword = text[len('/add_key '):].strip()
#     if keyword:
#         keywords.append(keyword)
#         send_message("Keyword added successfully.")
def add_keyword(user_id, keyword):
    if keyword:
        keywords.append(keyword)
        send_message("Keyword added successfully.")
    
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Insert the keyword into the table
    cursor.execute('INSERT INTO keywords (user_id, keyword) VALUES (?, ?)', (user_id, keyword))

    conn.commit()
    conn.close()
    
    message = send_message("Keyword added successfully.")
    
    send_message(user_id, message)

# # Function to get a keywords from the list
def get_keywords(user_id):
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Select all keywords for the specified user
    cursor.execute('SELECT keyword FROM keywords WHERE user_id = ?', (user_id,))
    keywords = [row[0] for row in cursor.fetchall()]

    conn.close()
    
    return keywords

# # Function to delete a keyword from the list
# def del_key(text):
#     keyword = text[len('/del_key '):].strip()
#     if keyword in keywords:
#         keywords.remove(keyword)
#         send_message("Keyword deleted successfully.")
#     else:
#         send_message("Keyword not found.")
def delete_keyword(user_id, keyword):
    
    if keyword not in get_keywords(user_id):
        send_message("Keyword not found.")
        return

    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Delete the keyword for the specified user
    cursor.execute('DELETE FROM keywords WHERE user_id = ? AND keyword = ?', (user_id, keyword))

    conn.commit()
    conn.close()
    
    send_message("Keyword deleted successfully.")


# Function to send a message to the chat
def send_message(user_id, message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': user_id, 'text': message}
    requests.post(url, data=data)

if __name__ == '__main__':
    app.run(port=5000)
    
#-----------------------------------------


#_---------------------------------------

# from flask import Flask, request
# import pprint
# import requests
# from decouple import config

# app = Flask(__name__)       # app 초기화 과정

# token = config('BOT_TOKEN')
# api_url = f'https://api.telegram.org/bot{token}'

# # http://127.0.0.1:5000/
# @app.route('/')  # Decorator  # root 디렉토리로 들어오면 happy hacking를 출력시킬거란 의미
# def root():
#     return '<h1>Happy Hacking!</h1>' \
#            '<h3>root 페이지입니다.</h3>'

# @app.route(f'/{token}', methods=['POST'])
# def telegram():    
#     # [1] 방식
#     response = request.get_json()
#     # print(request.get_json())  # 사용자가 텔레그램 웹에서 메시지를 보내면 flask 서버에서 프린트 된다.  # {'update_id': 385295894, 'message': {'message_id': 27, 'from': {'id': 728488945, 'is_bot': False, 'first_name': 'River', 'last_name': 'Kang', 'username': 'kangpro404', 'language_code': 'en'}, 'chat': {'id': 728488945, 'first_name': 'River', 'last_name': 'Kang', 'username': 'kangpro404', 'type': 'private'}, 'date': 1559530336, 'text': '11시 52분'}}
#     # 파일 보기가 좋지 않으니 파일 상단에 import pprint 해서 아래와 같이 사용하면 좋다.
#     pprint.pprint(request.get_json())
    
#     # JSON에서 사용자의 id 추출
#     chat_id = response['message']['from']['id']
#     print('사용자 아이디(chat_id): ', chat_id)
    
#     # JSON에서 사용자가 입력한 text 추출
#     chat_text = response['result']['message']['text']
#     print('사용자가 보낸 문자(chat_text): ', chat_text)
    
#     # 사용자가 입력한 걸 챗봇이 똑같이 출력
#     requests.get(f'{api_url}/sendMessage?chat_id={chat_id}&text={chat_text}')
#     #[2] 방식 - 사용자가 메시지를 입력했는지 안했는지 체크하고 결과를 출력하는 로직
#     pprint.pprint(request.get_json())
#     message = request.get_json().get('message')
#     if message is not None:
#         chat_id = message.get('from').get('id')
#         chat_text = message.get('text')
#         requests.get(f'{api_url}/sendMessage?chat_id={chat_id}&text={chat_text}')

#         # # 추가 예시
#         if text == 'hi':
#             # 점심메뉴를 확인하는 코드
#             text = '점심메뉴'
#         elif text == '로또':
#             # 로또를 확인하는 코드
#             text = '특정 로또번호'

#     return 'hello', 200

# # ※ 아래 함수?는 맨 아래에 둘 것!(위의 app.route 함수를 다 실행 한 뒤에 app.run 앱을 실행하겠다기 때문에)
# # python name.py로 설정할 수 있도록 설정방법
# # app.py 파일이 'python app.py'로 시작되었을 때 서버를 시작하겠다라는 의미.
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port='5000', debug=True)
#     # '서버가 실행이 되어있는동안 수정이 되면 자동으로 재시작을 하겠다'라는 의미
