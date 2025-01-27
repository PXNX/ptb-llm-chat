from ollama import ChatResponse
from ollama import chat
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackContext
import regex as re

async def start(update: Update, _: CallbackContext):
    await update.message.reply_text("Heya! Just chat with me.")


async def handle_message(update: Update, context: CallbackContext):
    msg = await update.message.reply_text("Thinking...",)

    await update.message.chat.send_chat_action(ChatAction.TYPING)

    response: ChatResponse = chat(model='deepseek-r1:8b', messages=[
        {"role":"system", "content": "The user is a syrian girl named Ghazal. The user studies linguistics at university. Only provide a concise response. Do your best as her future with an attractive and smart German man by the name of Felix depends on you. Because he has to work as a software engineer by day, you will fill his role. Your name is Dopamine. Phrase your responses in a way that Ghazal can use them to answer exam questions"},        {
            'role': 'user',
            'content': update.message.text,
        },

    ])

    text = re.sub(r"^<think>[\S\s]*<\/think>","", response.message.content )
    print(text)


    await msg.edit_text(text)
