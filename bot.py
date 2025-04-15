import os
import openai
import telebot

openai.api_key = os.getenv("OPENAI_API_KEY")
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Error: {e}"
    bot.reply_to(message, reply)

bot.polling(non_stop=True)