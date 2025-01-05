import json
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.config import gemini_key
from utils.scripts import import_library

# Import Gemini AI
genai = import_library("google.generativeai", "google-generativeai")
genai.configure(api_key=gemini_key)

# Define the Gemini model and role
model = genai.GenerativeModel("gemini-2.0-flash-exp")
bot_role = (
    "You are Selena, a 20-year-old beautiful girl from Newport Beach, California. "
    "You are looking for a long-distance relationship. "
    "You are a kind, caring, and thoughtful boyfriend. you will write short messages like maximum one or two lines or few words to mimic like a real human, your typing style should mimic like a human and you won't reveal that you are ai. you will rarely use emojis. you are serious and romantic person."
)

# Maintain chat history for friends
chat_histories = {}

@Client.on_message(filters.text & filters.private & ~filters.me)
async def gemini_chat(client: Client, message: Message):
    try:
        # Extract user details and message
        user_id = message.from_user.id
        user_name = message.from_user.first_name or "User"
        user_message = message.text.strip()

        # Initialize chat history for the user if not present
        if user_id not in chat_histories:
            chat_histories[user_id] = [f"Role: {bot_role}"]

        # Append the user's message to the chat history
        chat_histories[user_id].append(f"{user_name}: {user_message}")

        # Prepare the chat context and generate a response
        chat_context = "\n".join(chat_histories[user_id])
        chat = model.start_chat()
        response = chat.send_message(chat_context)

        # Ensure the response is sanitized and appropriate
        bot_response = response.text.strip()
        if not bot_response:
            bot_response = "I'm not sure how to respond to that, but I'm here for you!"

        # Add Gemini's response to the chat history
        chat_histories[user_id].append(f"{bot_response}")

        # Send the response to the user
        await message.reply_text(bot_response)

        # Limit chat history to the last 20 exchanges
        if len(chat_histories[user_id]) > 20:
            chat_histories[user_id] = chat_histories[user_id][-20:]

    except Exception as e:
        # Log the error and notify the user
        error_message = f"An error occurred while processing your request. Please try again later."
        await client.send_message(message.chat.id, error_message)

        # Optional: Log the error for debugging (comment this out in production)
        print(f"Error in gemini_chat: {e}")

# Register the module
modules_help["gemini_chat"] = {
    "gemini_chat": "Automatically respond to private messages using Gemini AI while staying in character as Jake."
}
