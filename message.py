from ollama import ChatResponse
from ollama import chat
from telegram import Update
from telegram.ext import CallbackContext


async def start(update: Update, _: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    msg = await update.message.reply_text("Thinking...")

    response: ChatResponse = chat(model='deepseek-r1:8b', messages=[
        {
            'role': 'user',
            'content': update.message.text,
        },
    ])


    text = response.message.content.replace("<think>","").replace("</think>","")
    print(text)
    await msg.edit_text(text)
