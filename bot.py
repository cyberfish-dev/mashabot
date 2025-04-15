import os
import requests
import telebot
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Handle text messages
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# Handle voice messages (.ogg)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Get voice file info
        file_info = bot.get_file(message.voice.file_id)
        file_url = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}'

        # Download .ogg file
        ogg_path = f"voice_{message.message_id}.ogg"
        with open(ogg_path, 'wb') as f:
            f.write(requests.get(file_url).content)

        # Transcribe with Whisper (supports ogg directly)
        with open(ogg_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        user_input = transcript.text

        # Get GPT response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )

        reply = response.choices[0].message.content
        bot.reply_to(message, f"🗣 You said: {user_input}\n\n🤖 {reply}")

        os.remove(ogg_path)  # Clean up

    except Exception as e:
        bot.reply_to(message, f"Voice error: {e}")

bot.polling(non_stop=True)