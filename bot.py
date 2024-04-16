import os
from flask import Flask, request
import telebot
from telebot.types import Update
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

chat_history = {}

def generate_response(prompt):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['text']
    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I couldn't generate a response at the moment."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Welcome to the ChatGPT Telegram bot.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        prompt = message.text
        chat_id = message.chat.id
        
        if chat_id not in chat_history:
            chat_history[chat_id] = ""
        
        chat_history[chat_id] += f"User: {prompt}\nAssistant: "
        
        response = generate_response(chat_history[chat_id])
        chat_history[chat_id] += f"{response}\n"
        
        bot.reply_to(message, response)
    except Exception as e:
        print("Error handling message:", e)
        bot.reply_to(message, "Sorry, something went wrong. Please try again.")


@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f'https://telegrambot3-17ht.onrender.com/{BOT_TOKEN}')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))