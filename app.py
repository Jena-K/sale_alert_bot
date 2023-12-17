# Import the config function from decouple
import requests
import subprocess, sqlite3

from flask import Flask, request
from decouple import config  

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


# Load the bot token and chat ID from the .env file
BOT_TOKEN = config('BOT_TOKEN')

# List to store keywords
keywords = []

# Initialize Flask app
app = Flask(__name__)

# Create db at first run
subprocess.run(['python', 'create_db.py'])

# Run get items
subprocess.Popen(['python', 'fm_keywords.py'])


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
            add_keyword(user_id, keyword)

        # Handle /del_key command
        elif text.startswith('/delkey '):
            delete_keyword(user_id, keyword)

    return 'success', 200

# Function to Insert a keywords into the table
def add_keyword(user_id, keyword):
    if keyword:
        keywords.append(keyword)
        send_message(user_id, "Keyword added successfully.")
    
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Insert the keyword into the table
    cursor.execute('INSERT INTO keywords (user_id, keyword) VALUES (?, ?)', (user_id, keyword))

    conn.commit()
    conn.close()
    
    message = send_message(user_id,  "Keyword added successfully.")
    
    send_message(user_id, message)

# Function to get a keywords from the table
def get_keywords(user_id):
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Select all keywords for the specified user
    cursor.execute('SELECT keyword FROM keywords WHERE user_id = ?', (user_id,))
    keywords = [row[0] for row in cursor.fetchall()]

    conn.close()
    
    return keywords

# Function to Delete a keywords to the table
def delete_keyword(user_id, keyword):
    
    if keyword not in get_keywords(user_id):
        send_message(user_id, "Keyword not found.")
        return

    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Delete the keyword for the specified user
    cursor.execute('DELETE FROM keywords WHERE user_id = ? AND keyword = ?', (user_id, keyword))

    conn.commit()
    conn.close()
    
    send_message(user_id, "Keyword deleted successfully.")


# Function to send a message to the chat
def send_message(user_id, message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': user_id, 'text': message}
    requests.post(url, data=data)

if __name__ == '__main__':
    app.run(port=5000)
    
