import os
import yt_dlp
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)

# Function to handle start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! I can help you download YouTube videos. Please send me a YouTube video link.")

# Function to handle text message
@bot.message_handler(func=lambda message: True)
def download_video(message):
    try:
        url = message.text
        chat_id = message.chat.id
        # Create keyboard to select format
        markup = types.ReplyKeyboardMarkup(row_width=2)
        mp4_button = types.KeyboardButton('MP4')
        mp3_button = types.KeyboardButton('MP3')
        markup.add(mp4_button, mp3_button)
        bot.send_message(chat_id, "Please select the format:", reply_markup=markup)
        bot.register_next_step_handler(message, process_format, url)
    except Exception as e:
        bot.reply_to(message, f"Sorry, there was an error. {e}")

# Function to handle format selection
def process_format(message, url):
    try:
        chat_id = message.chat.id
        format = message.text.lower()
        if format == 'mp4':
            ydl_opts = {'outtmpl': '%(title)s.%(ext)s'}
        elif format == 'mp3':
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict)
            ydl.download([url])
            file = open(filename, 'rb')
            bot.send_document(chat_id, file)
    except Exception as e:
        bot.reply_to(message, f"Sorry, there was an error. {e}")

# Start the bot
bot.polling()
