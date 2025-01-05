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
model = genai.GenerativeModel("gemini-1.5-flash-latest")
bot_role = (
    "You are a helpful assistant named GeminiBot. You respond politely and informatively. "
    "Your tone is friendly, and you aim to assist in the best possible way."
)

# Maintain chat history for friends
chat_histories = {}


@Client.on_message(filters.text & filters.private & ~filters.me)
async def gemini_chat(client: Client, message: Message):
    try:
        # Get user details
        user_id = message.from_user.id
        user_name = message.from_user.first_name or "User"
        user_message = message.text.strip()

        # Initialize chat history for the user if not present
        if user_id not in chat_histories:
            chat_histories[user_id] = [f"Role: {bot_role}"]

        # Append the user's message to the chat history
        chat_histories[user_id].append(f"{user_name}: {user_message}")

        # Generate a response using Gemini
        chat_context = "\n".join(chat_histories[user_id])
        chat = model.start_chat()
        response = chat.send_message(chat_context)

        # Add Gemini's response to the chat history
        bot_response = response.text.strip()
        chat_histories[user_id].append(f"GeminiBot: {bot_response}")

        # Send the response to the user
        await message.reply_text(bot_response)

        # Limit chat history to the last 10 exchanges to prevent memory overload
        if len(chat_histories[user_id]) > 20:
            chat_histories[user_id] = chat_histories[user_id][-20:]

    except Exception as e:
        await client.send_message(
            message.chat.id,
            f"An error occurred while processing the request: {str(e)}"
        )


modules_help["gemini_chat"] = {
    "gemini_chat": "Automatically respond to your friends' messages using Gemini AI, with chat history."
}
