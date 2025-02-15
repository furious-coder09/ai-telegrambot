from PIL import Image
from io import BytesIO
import telebot
import google.generativeai as genai
from google.genai import types

# Initialize the Gemini AI client
genai.configure(api_key="YOUR_GEMINI_APIKEY")  # Replace with your actual API key

# Initialize the Telegram bot
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your actual bot token
bot = telebot.TeleBot(BOT_TOKEN)



@bot.message_handler(content_types=['text'])
def handle_text(message):
    """
    Handles text messages sent by users and sends them to Gemini AI.
    """
    user_text = message.text  # Extract text from user message

    # Send the text to Gemini AI
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([user_text])
    
    # Send the AI's response back to the user
    bot.send_message(message.chat.id, response.text)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """
    Handles images sent by the user.
    Extracts the image and caption, sends them to the Gemini model,
    and returns the response to the user.
    """
    text = message.caption if message.caption else ""  # Get caption if available
    photo = message.photo[-1]  # Get the highest-resolution photo
    file_id = photo.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Open the image from memory
    image = Image.open(BytesIO(downloaded_file))

    # Send to Gemini AI
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([
        text, image
    ])
    
    bot.send_message(message.chat.id, response.text)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    """
    Handles voice messages (OGG format) sent by users, sends them to Gemini AI,
    and returns the AI-generated response.
    """
    file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
    file_info = bot.get_file(file_id)  # Get file info from Telegram
    downloaded_file = bot.download_file(file_info.file_path)  # Download the file

    # Open the OGG file from memory
    audio_file = BytesIO(downloaded_file)

    # Upload the file to Gemini AI
    gemini_file = genai.upload_file(audio_file, display_name="audio.ogg", mime_type="audio/ogg")

    # If there's a caption, use it as the query; otherwise, use a default prompt
    user_prompt = message.caption if message.caption else "Listen to this audio and answer any questions asked in it,you should respond with the answers to the questions asked in the audio"


    # Send the audio file for processing
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content([
        user_prompt,
        gemini_file
    ])

    # Send AI's response back to the user
    bot.send_message(message.chat.id, response.text)

# Start the bot
bot.infinity_polling()
