import os
from flask import Flask, request
import telebot
from telebot.types import Update
import openai

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_KEY = os.environ.get('OPENAI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_KEY

chat_history = {}

def generate_response(prompt, chat_id):
    chat_history.setdefault(chat_id, '')
    chat_history[chat_id] += f"User: {prompt}\nAssistant: "
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=chat_history[chat_id],
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    reply = response.choices[0].text.strip()
    chat_history[chat_id] += f"{reply}\n"
    return reply

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Welcome to the ChatGPT Telegram bot.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        reply = generate_response(message.text, message.chat.id)
        bot.reply_to(message, reply)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Sorry, something went wrong. Please try again.")

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f'https://{os.environ.get("RENDER_EXTERNAL_URL")}/{BOT_TOKEN}')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
